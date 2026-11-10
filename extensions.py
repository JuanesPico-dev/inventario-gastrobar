"""
Aquí viven las DOS conexiones de la app (persistencia políglota):
  - db    -> SQLAlchemy, habla con MySQL
  - mongo -> pymongo, habla con MongoDB
Las demás partes del proyecto importan desde aquí.
"""
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient, DESCENDING
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()  

class Mongo:
    """Envoltura sencilla para tener la base de Mongo a mano en toda la app."""

    def __init__(self):
        self.client = None
        self.db = None

    def init_app(self, app):
        uri = app.config["MONGO_URI"]
        if uri.startswith("mongomock://"):
            # Modo prueba: Mongo "falso" en memoria, misma API que pymongo
            import mongomock
            self.client = mongomock.MongoClient()
        else:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.db = self.client[app.config["MONGO_DB"]]
        self.crear_indices()

    def crear_indices(self):
        # Los índices hacen rápidas las consultas que más usamos
        # (ej: "últimos 10 movimientos de un producto")
        self.db.movimientos_inventario.create_index(
            [("producto_id", 1), ("fecha", DESCENDING)]
        )
        self.db.fichas_producto.create_index("producto_id", unique=True)
        self.db.logs_actividad.create_index([("fecha", DESCENDING)])

    # atajos para no escribir mongo.db.xxxx en todo lado
    @property
    def movimientos(self):
        return self.db.movimientos_inventario

    @property
    def fichas(self):
        return self.db.fichas_producto

    @property
    def logs(self):
        return self.db.logs_actividad


mongo = Mongo()
