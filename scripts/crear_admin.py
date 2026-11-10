"""
Crea (o promueve) el primer administrador.
Como por /api/auth/registro todos entran como empleado, el primer admin
se crea desde aquí, con acceso directo al servidor.

    python scripts/crear_admin.py
"""
import os
import sys
from getpass import getpass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # noqa: E402
from extensions import db  # noqa: E402
from models import Usuario  # noqa: E402

with app.app_context():
    email = input("Email del admin: ").strip().lower()
    u = Usuario.query.filter_by(email=email).first()
    if u:
        u.rol = "admin"
        u.activo = True
        print(f"{email} ya existía, ahora es admin.")
    else:
        nombre = input("Nombre: ").strip()
        clave = getpass("Contraseña (mínimo 8, no se ve al escribir): ")
        if len(clave) < 8:
            sys.exit("La contraseña debe tener mínimo 8 caracteres")
        u = Usuario(nombre=nombre, email=email, rol="admin")
        u.set_password(clave)
        db.session.add(u)
        print(f"Admin {email} creado.")
    db.session.commit()
