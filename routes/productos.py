"""
CRUD de productos (MySQL)
+ el endpoint estrella que COMBINA SQL y NoSQL: /api/productos/<id>/detalle
"""
from flask import Blueprint, request, jsonify
from pymongo import DESCENDING
from extensions import db, mongo
from models import Producto, Categoria
from utils import error, registrar_log, doc_a_json

bp = Blueprint("productos", __name__, url_prefix="/api/productos")

CAMPOS = ["codigo_barras", "nombre", "unidad", "precio_compra", "precio_venta",
          "stock_minimo", "categoria_id", "proveedor_id", "activo"]


@bp.get("")
def listar():
    # filtro opcional: /api/productos?categoria_id=2
    q = Producto.query
    if request.args.get("categoria_id"):
        q = q.filter_by(categoria_id=request.args.get("categoria_id", type=int))
    return jsonify([p.to_dict() for p in q.order_by(Producto.nombre).all()])


@bp.get("/<int:id>")
def obtener(id):
    p = db.session.get(Producto, id)
    return jsonify(p.to_dict()) if p else error("Producto no encontrado", 404)


@bp.post("")
def crear():
    data = request.get_json() or {}
    if not data.get("nombre") or not data.get("categoria_id"):
        return error("nombre y categoria_id son obligatorios")
    if not db.session.get(Categoria, data["categoria_id"]):
        return error("La categoría no existe", 404)

    p = Producto(**{k: data[k] for k in CAMPOS if k in data})
    # el stock inicial se guarda, pero de ahí en adelante solo cambia con movimientos
    p.stock_actual = int(data.get("stock_actual", 0))
    db.session.add(p)
    db.session.commit()
    registrar_log("CREAR", "producto", p.id, {"nombre": p.nombre})
    return jsonify(p.to_dict()), 201


@bp.put("/<int:id>")
def actualizar(id):
    p = db.session.get(Producto, id)
    if not p:
        return error("Producto no encontrado", 404)
    data = request.get_json() or {}
    if "stock_actual" in data:
        return error("El stock no se edita directo, registre un movimiento (POST /api/movimientos)")
    for k in CAMPOS:
        if k in data:
            setattr(p, k, data[k])
    db.session.commit()
    registrar_log("ACTUALIZAR", "producto", p.id, data)
    return jsonify(p.to_dict())


@bp.delete("/<int:id>")
def eliminar(id):
    p = db.session.get(Producto, id)
    if not p:
        return error("Producto no encontrado", 404)
    db.session.delete(p)
    db.session.commit()
    # al borrar el producto también borramos su ficha en Mongo
    # (los movimientos se dejan como historial)
    mongo.fichas.delete_one({"producto_id": id})
    registrar_log("ELIMINAR", "producto", id)
    return jsonify({"mensaje": "Producto eliminado"})


# ------------------------------------------------------------------
#  ENDPOINT QUE COMBINA SQL + NoSQL
# ------------------------------------------------------------------
@bp.get("/<int:id>/detalle")
def detalle(id):
    """
    Junta en una sola respuesta:
      1. Datos fijos del producto  -> MySQL (tabla productos + categoria + proveedor)
      2. Ficha con atributos variables -> MongoDB (fichas_producto)
      3. Últimos 10 movimientos de inventario -> MongoDB (movimientos_inventario)
    La "llave" que une los dos mundos es producto_id.
    """
    limite = request.args.get("limite", 10, type=int)

    # 1) SQL
    p = db.session.get(Producto, id)
    if not p:
        return error("Producto no encontrado", 404)
    producto = p.to_dict()
    producto["proveedor"] = p.proveedor.to_dict() if p.proveedor else None
    producto["alerta_stock_bajo"] = p.stock_actual <= p.stock_minimo

    # 2) NoSQL: ficha
    ficha = mongo.fichas.find_one({"producto_id": id}, {"_id": 0, "producto_id": 0})

    # 3) NoSQL: últimos movimientos (usa el índice producto_id + fecha)
    cursor = (mongo.movimientos.find({"producto_id": id})
              .sort("fecha", DESCENDING).limit(limite))
    movimientos = [doc_a_json(m) for m in cursor]

    return jsonify({
        "producto": producto,                       # viene de MySQL
        "ficha": doc_a_json(ficha) if ficha else None,  # viene de MongoDB
        "ultimos_movimientos": movimientos,         # viene de MongoDB
        "fuentes": {"producto": "MySQL", "ficha": "MongoDB", "ultimos_movimientos": "MongoDB"},
    })
