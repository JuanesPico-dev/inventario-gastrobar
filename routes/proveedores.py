"""CRUD de proveedores (MySQL)."""
from flask import Blueprint, request, jsonify
from extensions import db
from models import Proveedor
from seguridad import rol_requerido
from utils import error, registrar_log

bp = Blueprint("proveedores", __name__, url_prefix="/api/proveedores")

CAMPOS = ["nombre", "nit", "telefono", "email"]


@bp.get("")
@rol_requerido()
def listar():
    return jsonify([p.to_dict() for p in Proveedor.query.order_by(Proveedor.nombre).all()])


@bp.get("/<int:id>")
@rol_requerido()
def obtener(id):
    p = db.session.get(Proveedor, id)
    return jsonify(p.to_dict()) if p else error("Proveedor no encontrado", 404)


@bp.post("")
@rol_requerido("admin")
def crear():
    data = request.get_json() or {}
    if not data.get("nombre"):
        return error("El nombre es obligatorio")
    p = Proveedor(**{k: data.get(k) for k in CAMPOS})
    db.session.add(p)
    db.session.commit()
    registrar_log("CREAR", "proveedor", p.id, p.to_dict())
    return jsonify(p.to_dict()), 201


@bp.put("/<int:id>")
@rol_requerido("admin")
def actualizar(id):
    p = db.session.get(Proveedor, id)
    if not p:
        return error("Proveedor no encontrado", 404)
    data = request.get_json() or {}
    for k in CAMPOS:
        if k in data:
            setattr(p, k, data[k])
    db.session.commit()
    registrar_log("ACTUALIZAR", "proveedor", p.id, data)
    return jsonify(p.to_dict())


@bp.delete("/<int:id>")
@rol_requerido("admin")
def eliminar(id):
    p = db.session.get(Proveedor, id)
    if not p:
        return error("Proveedor no encontrado", 404)
    if p.productos:
        return error("No se puede borrar: el proveedor tiene productos asociados", 409)
    db.session.delete(p)
    db.session.commit()
    registrar_log("ELIMINAR", "proveedor", id)
    return jsonify({"mensaje": "Proveedor eliminado"})
