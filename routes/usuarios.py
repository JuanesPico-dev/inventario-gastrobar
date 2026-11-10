"""Gestión de usuarios (solo admin)."""
from flask import Blueprint, request, jsonify, g
from extensions import db
from models import Usuario
from seguridad import rol_requerido
from utils import error, registrar_log

bp = Blueprint("usuarios", __name__, url_prefix="/api/usuarios")

ROLES = ("admin", "empleado")


@bp.get("")
@rol_requerido("admin")
def listar():
    return jsonify([u.to_dict() for u in Usuario.query.order_by(Usuario.id).all()])


@bp.put("/<int:id>")
@rol_requerido("admin")
def actualizar(id):
    """Cambiar rol y/o activar-desactivar. Body: {"rol": "admin"} o {"activo": false}"""
    u = db.session.get(Usuario, id)
    if not u:
        return error("Usuario no encontrado", 404)
    data = request.get_json() or {}

    if u.id == g.usuario.id:
        # evita que el admin se quite el permiso a sí mismo y deje el sistema sin admin
        return error("No puedes cambiar tu propio rol ni desactivarte", 409)
    if "rol" in data:
        if data["rol"] not in ROLES:
            return error(f"rol debe ser uno de: {', '.join(ROLES)}")
        u.rol = data["rol"]
    if "activo" in data:
        u.activo = bool(data["activo"])

    db.session.commit()
    registrar_log("ACTUALIZAR", "usuario", u.id, data, usuario=g.usuario.email)
    return jsonify(u.to_dict())
