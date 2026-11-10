"""
Configuración de la app.
Los datos de conexión NO van quemados en el código, se leen del archivo .env
(así no subimos claves a GitHub).
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Conexión a MySQL (datos estructurados)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQL_URI", "mysql+pymysql://root:@localhost:3306/inventario_gastrobar"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Conexión a MongoDB (datos dinámicos / de alta frecuencia)
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB = os.getenv("MONGO_DB", "inventario_gastrobar")

    # JWT (autenticación)
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "cambiar-en-produccion")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)   # el token dura un turno de trabajo

    JSON_SORT_KEYS = False