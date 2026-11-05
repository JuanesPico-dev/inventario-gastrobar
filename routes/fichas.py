"""
Fichas de producto (MongoDB) — atributos VARIABLES de cada producto.

Ejemplos de por qué no sirven columnas fijas:
  Cerveza   -> grados_alcohol, volumen_ml, tipo (lager, IPA), retornable
  Licor     -> grados_alcohol, volumen_ml, origen, anos_anejamiento
  Comida    -> alergenos, peso_g, requiere_refrigeracion, vida_util_dias
  Desechable-> material, unidades_por_paquete
Si esto fuera SQL tocaría una tabla con 30 columnas casi todas en NULL.
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from extensions import db, mongo
from models import Producto
from utils import error, registrar_log, doc_a_json

bp = Blueprint("fichas", __name__, url_prefix="/api/fichas")


@bp.get("")
def listar():
    """?tipo=cerveza  o  ?etiqueta=importado"""
    filtro = {}
    if request.args.get("tipo"):
        filtro["tipo"] = request.args["tipo"]
    if request.args.get("etiqueta"):
        filtro["etiquetas"] = request.args["etiqueta"]  # busca dentro del arreglo
    return jsonify([doc_a_json(d) for d in mongo.fichas.find(filtro)])


@bp.get("/<int:producto_id>")
def obtener(producto_id):
    doc = mongo.fichas.find_one({"producto_id": producto_id})
    return jsonify(doc_a_json(doc)) if doc else error("Ficha no encontrada", 404)


@bp.post("")
def crear():
    data = request.get_json() or {}
    producto_id = data.get("producto_id")
    # la ficha solo puede existir si el producto existe en MySQL
    if not db.session.get(Producto, producto_id):
        return error("El producto no existe en la base SQL", 404)
    if mongo.fichas.find_one({"producto_id": producto_id}):
        return error("Ese producto ya tiene ficha, use PUT", 409)

    doc = {
        "producto_id": producto_id,
        "tipo": data.get("tipo", "general"),
        "atributos": data.get("atributos", {}),   # <- lo que sea, distinto por producto
        "etiquetas": data.get("etiquetas", []),
        "notas": data.get("notas"),
        "actualizado": datetime.utcnow(),
    }
    res = mongo.fichas.insert_one(doc)
    doc["_id"] = res.inserted_id
    registrar_log("CREAR", "ficha", producto_id, {"tipo": doc["tipo"]})
    return jsonify(doc_a_json(doc)), 201


@bp.put("/<int:producto_id>")
def actualizar(producto_id):
    """Se pueden mandar atributos nuevos sin tocar la estructura de nada."""
    if not mongo.fichas.find_one({"producto_id": producto_id}):
        return error("Ficha no encontrada", 404)
    data = request.get_json() or {}
    cambios = {"actualizado": datetime.utcnow()}
    for k in ("tipo", "etiquetas", "notas"):
        if k in data:
            cambios[k] = data[k]
    # los atributos se mezclan uno a uno (no se borran los que ya estaban)
    for k, v in (data.get("atributos") or {}).items():
        cambios[f"atributos.{k}"] = v
    mongo.fichas.update_one({"producto_id": producto_id}, {"$set": cambios})
    registrar_log("ACTUALIZAR", "ficha", producto_id, data)
    return jsonify(doc_a_json(mongo.fichas.find_one({"producto_id": producto_id})))


@bp.delete("/<int:producto_id>")
def eliminar(producto_id):
    res = mongo.fichas.delete_one({"producto_id": producto_id})
    if res.deleted_count == 0:
        return error("Ficha no encontrada", 404)
    registrar_log("ELIMINAR", "ficha", producto_id)
    return jsonify({"mensaje": "Ficha eliminada"})
