"""Autenticación: registro, login y perfil del usuario."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db
from models import Usuario
from utils import error, registrar_log

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/registro")
def registro():
    data = request.get_json() or {}
    nombre = (data.get("nombre") or "").strip()
    email = (data.get("email") or "").strip().lower()
    clave = data.get("password") or ""

    if not nombre or not email or not clave:
        return error("nombre, email y password son obligatorios")
    if len(clave) < 8:
        return error("La contraseña debe tener mínimo 8 caracteres")
    if Usuario.query.filter_by(email=email).first():
        return error("Ya existe un usuario con ese email", 409)

    # El rol NO se recibe del cliente: todos se registran como empleado.
    # Solo un admin puede subir a alguien a admin.
    u = Usuario(nombre=nombre, email=email, rol="empleado")
    u.set_password(clave)
    db.session.add(u)
    db.session.commit()
    registrar_log("REGISTRO", "usuario", u.id, {"email": email})
    return jsonify(u.to_dict()), 201


@bp.post("/login")
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    clave = data.get("password") or ""

    u = Usuario.query.filter_by(email=email).first()
    if not u or not u.check_password(clave):
        registrar_log("LOGIN_FALLIDO", "usuario", None, {"email": email})
        # mensaje genérico: no le decimos al atacante si el email existe
        return error("Credenciales inválidas", 401)
    if not u.activo:
        return error("Usuario inactivo", 403)

    token = create_access_token(identity=str(u.id), additional_claims={"rol": u.rol})
    registrar_log("LOGIN", "usuario", u.id, {"email": email}, usuario=email)
    return jsonify({"access_token": token, "usuario": u.to_dict()})


@bp.get("/yo")
@jwt_required()
def yo():
    """Devuelve el usuario dueño del token."""
    u = db.session.get(Usuario, int(get_jwt_identity()))
    return jsonify(u.to_dict()) if u else error("Usuario no encontrado", 404)
