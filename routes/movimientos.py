"""
Movimientos de inventario (MongoDB) — CRUD + lógica de negocio con MySQL.

Cada vez que entra o sale algo del gastrobar se crea un movimiento.
Son MUCHOS registros (alta frecuencia) y cada tipo trae datos diferentes:
  - entrada: factura del proveedor, lote, fecha de vencimiento...
  - salida:  mesa, mesero, número de comanda...
  - merma:   causa (se rompió, se venció, se derramó)...
Por eso van en Mongo, pero el stock oficial vive en MySQL.
"""
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, g
from pymongo import DESCENDING
from extensions import db, mongo
from models import Producto
from seguridad import rol_requerido
from utils import error, registrar_log, doc_a_json, id_valido

bp = Blueprint("movimientos", __name__, url_prefix="/api/movimientos")

TIPOS = {"entrada": 1, "salida": -1, "merma": -1, "ajuste": 1}  # signo sobre el stock


@bp.get("")
@rol_requerido()
def listar():
    """Filtros opcionales: ?producto_id=1&tipo=salida&dias=7&limite=50"""
    filtro = {}
    if request.args.get("producto_id"):
        filtro["producto_id"] = request.args.get("producto_id", type=int)
    if request.args.get("tipo"):
        filtro["tipo"] = request.args["tipo"]
    if request.args.get("dias"):
        desde = datetime.utcnow() - timedelta(days=request.args.get("dias", type=int))
        filtro["fecha"] = {"$gte": desde}
    limite = request.args.get("limite", 50, type=int)
    docs = mongo.movimientos.find(filtro).sort("fecha", DESCENDING).limit(limite)
    return jsonify([doc_a_json(d) for d in docs])


@bp.get("/<id>")
@rol_requerido()
def obtener(id):
    oid = id_valido(id)
    doc = mongo.movimientos.find_one({"_id": oid}) if oid else None
    return jsonify(doc_a_json(doc)) if doc else error("Movimiento no encontrado", 404)


@bp.post("")
@rol_requerido()
def crear():
    """
    LÓGICA DE NEGOCIO QUE TOCA LAS DOS BASES:
      1. Valida en MySQL que el producto exista y esté activo.
      2. Calcula el nuevo stock y valida que no quede negativo.
      3. Actualiza el stock en MySQL (sin confirmar todavía).
      4. Guarda el movimiento en MongoDB.
      5. Si todo salió bien -> commit en MySQL. Si Mongo falla -> rollback.
    """
    data = request.get_json() or {}
    tipo = data.get("tipo")
    producto_id = data.get("producto_id")
    cantidad = data.get("cantidad")

    if tipo not in TIPOS:
        return error(f"tipo debe ser uno de: {', '.join(TIPOS)}")
    # RBAC: el empleado solo registra ventas y pérdidas
    if g.usuario.rol != "admin" and tipo not in ("salida", "merma"):
        return error("Un empleado solo puede registrar salidas y mermas", 403)
    if not isinstance(cantidad, int) or cantidad == 0:
        return error("cantidad debe ser un entero distinto de 0")
    if tipo != "ajuste" and cantidad < 0:
        return error("cantidad debe ser positiva (el tipo ya dice si suma o resta)")

    # 1) MySQL
    producto = db.session.get(Producto, producto_id)
    if not producto or not producto.activo:
        return error("Producto no existe o está inactivo", 404)

    # 2) nuevo stock
    variacion = cantidad * TIPOS[tipo]
    nuevo_stock = producto.stock_actual + variacion
    if nuevo_stock < 0:
        return error(f"Stock insuficiente. Hay {producto.stock_actual} {producto.unidad}(s)", 409)

    # 3) MySQL: cambiamos el stock pero aún sin commit
    stock_anterior = producto.stock_actual
    producto.stock_actual = nuevo_stock

    documento = {
        "producto_id": producto.id,
        "producto_nombre": producto.nombre,   # copia para leer el historial sin ir a SQL
        "tipo": tipo,
        "cantidad": cantidad,
        "stock_anterior": stock_anterior,
        "stock_resultante": nuevo_stock,
        "usuario": g.usuario.email,        # sale del token, no del body
        "motivo": data.get("motivo"),
        "detalle": data.get("detalle", {}),   # <- campo libre, cambia según el tipo
        "fecha": datetime.utcnow(),
    }

    try:
        # 4) MongoDB
        resultado = mongo.movimientos.insert_one(documento)
        # 5) confirmamos MySQL
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error(f"No se pudo registrar el movimiento: {e}", 500)

    documento["_id"] = resultado.inserted_id
    registrar_log("CREAR", "movimiento", str(resultado.inserted_id),
                  {"producto_id": producto.id, "tipo": tipo, "cantidad": cantidad},
                  usuario=documento["usuario"])

    respuesta = doc_a_json(documento)
    respuesta["alerta_stock_bajo"] = nuevo_stock <= producto.stock_minimo
    return jsonify(respuesta), 201


@bp.put("/<id>")
@rol_requerido("admin")
def actualizar(id):
    """Solo deja corregir motivo y detalle. La cantidad NO se edita
    (si se equivocaron, se anula el movimiento y se crea otro)."""
    oid = id_valido(id)
    if not oid or not mongo.movimientos.find_one({"_id": oid}):
        return error("Movimiento no encontrado", 404)
    data = request.get_json() or {}
    cambios = {k: data[k] for k in ("motivo", "detalle") if k in data}
    if not cambios:
        return error("Solo se puede modificar 'motivo' y/o 'detalle'")
    cambios["editado_en"] = datetime.utcnow()
    mongo.movimientos.update_one({"_id": oid}, {"$set": cambios})
    registrar_log("ACTUALIZAR", "movimiento", id, data, usuario=g.usuario.email)
    return jsonify(doc_a_json(mongo.movimientos.find_one({"_id": oid})))


@bp.delete("/<id>")
@rol_requerido("admin")
def eliminar(id):
    """Anula un movimiento: devuelve el stock en MySQL y lo borra de Mongo."""
    oid = id_valido(id)
    mov = mongo.movimientos.find_one({"_id": oid}) if oid else None
    if not mov:
        return error("Movimiento no encontrado", 404)

    producto = db.session.get(Producto, mov["producto_id"])
    if producto:
        revertido = producto.stock_actual - mov["cantidad"] * TIPOS[mov["tipo"]]
        if revertido < 0:
            return error("No se puede anular: el stock quedaría negativo", 409)
        producto.stock_actual = revertido
    try:
        mongo.movimientos.delete_one({"_id": oid})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error(f"No se pudo anular: {e}", 500)

    registrar_log("ELIMINAR", "movimiento", id, {"producto_id": mov["producto_id"]}, usuario=g.usuario.email)
    return jsonify({"mensaje": "Movimiento anulado y stock revertido",
                    "stock_actual": producto.stock_actual if producto else None})
