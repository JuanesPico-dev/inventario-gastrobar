"""CRUD de categorías (MySQL)."""
from flask import Blueprint, request, jsonify
from extensions import db
from models import Categoria
from seguridad import rol_requerido
from utils import error, registrar_log

bp = Blueprint("categorias", __name__, url_prefix="/api/categorias")


@bp.get("")
@rol_requerido()
def listar():
    return jsonify([c.to_dict() for c in Categoria.query.order_by(Categoria.nombre).all()])


@bp.get("/<int:id>")
@rol_requerido()
def obtener(id):
    c = db.session.get(Categoria, id)
    return jsonify(c.to_dict()) if c else error("Categoría no encontrada", 404)


@bp.post("")
@rol_requerido("admin")
def crear():
    data = request.get_json() or {}
    if not data.get("nombre"):
        return error("El nombre es obligatorio")
    c = Categoria(nombre=data["nombre"], descripcion=data.get("descripcion"))
    db.session.add(c)
    db.session.commit()
    registrar_log("CREAR", "categoria", c.id, c.to_dict())
    return jsonify(c.to_dict()), 201


@bp.put("/<int:id>")
@rol_requerido("admin")
def actualizar(id):
    c = db.session.get(Categoria, id)
    if not c:
        return error("Categoría no encontrada", 404)
    data = request.get_json() or {}
    c.nombre = data.get("nombre", c.nombre)
    c.descripcion = data.get("descripcion", c.descripcion)
    db.session.commit()
    registrar_log("ACTUALIZAR", "categoria", c.id, data)
    return jsonify(c.to_dict())


@bp.delete("/<int:id>")
@rol_requerido("admin")
def eliminar(id):
    c = db.session.get(Categoria, id)
    if not c:
        return error("Categoría no encontrada", 404)
    if c.productos:
        return error("No se puede borrar: la categoría tiene productos", 409)
    db.session.delete(c)
    db.session.commit()
    registrar_log("ELIMINAR", "categoria", id)
    return jsonify({"mensaje": "Categoría eliminada"})
