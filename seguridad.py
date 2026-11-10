"""
Seguridad: el "candado" que se le pone a cada ruta.

    @rol_requerido()                    -> cualquier usuario con sesión iniciada
    @rol_requerido("admin")             -> solo administradores
    @rol_requerido("admin", "empleado") -> cualquiera de esos dos roles
"""
from functools import wraps
from flask import g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from extensions import db
from models import Usuario
from utils import error


def rol_requerido(*roles):
    def decorador(funcion):
        @wraps(funcion)
        def envoltura(*args, **kwargs):
            # 1. ¿Trae un token válido? (si no, flask-jwt-extended responde 401)
            verify_jwt_in_request()

            # 2. Buscamos al usuario en MySQL. Así, si el admin lo desactiva
            #    o le cambia el rol, el cambio aplica de inmediato aunque
            #    el token todavía no haya vencido.
            usuario = db.session.get(Usuario, int(get_jwt_identity()))
            if not usuario or not usuario.activo:
                return error("Usuario inactivo o inexistente", 401)

            # 3. ¿Tiene el rol que pide la ruta?
            if roles and usuario.rol not in roles:
                return error(f"Acceso denegado: se requiere rol {' o '.join(roles)}", 403)

            g.usuario = usuario   # queda disponible dentro de la ruta
            return funcion(*args, **kwargs)
        return envoltura
    return decorador
