"""Funciones de apoyo que usan varias rutas."""
from datetime import datetime
from bson import ObjectId
from flask import jsonify
from extensions import mongo


def error(mensaje, codigo=400):
    return jsonify({"error": mensaje}), codigo


def doc_a_json(doc):
    """Mongo guarda el _id como ObjectId y las fechas como datetime.
    JSON no entiende esos tipos, así que los pasamos a texto."""
    if doc is None:
        return None
    doc = dict(doc)
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    for k, v in doc.items():
        if isinstance(v, datetime):
            doc[k] = v.isoformat()
    return doc


def id_valido(id_texto):
    """Convierte el texto de la URL en ObjectId (o None si no sirve)."""
    try:
        return ObjectId(id_texto)
    except Exception:
        return None


def registrar_log(accion, entidad, entidad_id=None, datos=None, usuario="sistema"):
    """Guarda en Mongo un registro de lo que pasó en la app.
    Cada log puede traer 'datos' distintos, por eso va en NoSQL."""
    mongo.logs.insert_one({
        "accion": accion,          # CREAR, ACTUALIZAR, ELIMINAR...
        "entidad": entidad,        # producto, movimiento, ficha...
        "entidad_id": entidad_id,
        "usuario": usuario,
        "datos": datos or {},
        "fecha": datetime.utcnow(),
    })
