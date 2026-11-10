"""
Sistema de Gestión de Inventario - Gastrobar
Curso Nuevas Tecnologías de Desarrollo - Entrega 2 (SQL + NoSQL)

Para correr:  python app.py   ->  http://localhost:5000
"""
from flask import Flask, jsonify
from config import Config
from extensions import db, mongo, jwt


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.json.ensure_ascii = False   # para que las tildes salgan bien en el JSON
    app.json.sort_keys = False

    # Conectamos las dos bases de datos
    db.init_app(app)      # MySQL
    mongo.init_app(app)   # MongoDB
    jwt.init_app(app)     # JWT

    # Registramos las rutas (blueprints)
    from routes import auth, usuarios, categorias, proveedores, productos, movimientos, fichas, reportes
    for modulo in (auth, usuarios, categorias, proveedores, productos, movimientos, fichas, reportes):
        app.register_blueprint(modulo.bp)

    with app.app_context():
        db.create_all()   # crea las tablas en MySQL si no existen

    @app.get("/")
    def inicio():
        return jsonify({"app": "Inventario Gastrobar", "estado": "ok"})

    @app.get("/api/salud")
    def salud():
        """Revisa que las DOS bases respondan."""
        estado = {}
        try:
            db.session.execute(db.text("SELECT 1"))
            estado["mysql"] = "conectado"
        except Exception as e:
            estado["mysql"] = f"error: {e}"
        try:
            mongo.client.admin.command("ping")
            estado["mongodb"] = "conectado"
        except Exception as e:
            estado["mongodb"] = f"error: {e}"
        return jsonify(estado)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
