"""
Modelos SQL (MySQL) con SQLAlchemy.

Aquí va lo ESTRUCTURADO: datos que siempre tienen las mismas columnas
y que se relacionan entre sí con llaves foráneas.

  categorias 1 ---- N productos N ---- 1 proveedores
"""
from datetime import datetime
from extensions import db


class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(60), nullable=False, unique=True)
    descripcion = db.Column(db.String(200))

    productos = db.relationship("Producto", back_populates="categoria")

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre, "descripcion": self.descripcion}


class Proveedor(db.Model):
    __tablename__ = "proveedores"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    nit = db.Column(db.String(20), unique=True)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))

    productos = db.relationship("Producto", back_populates="proveedor")

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "nit": self.nit,
            "telefono": self.telefono,
            "email": self.email,
        }


class Producto(db.Model):
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)
    codigo_barras = db.Column(db.String(30), unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    unidad = db.Column(db.String(20), nullable=False, default="unidad")  # unidad, botella, kg...
    precio_compra = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    precio_venta = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    stock_actual = db.Column(db.Integer, nullable=False, default=0)
    stock_minimo = db.Column(db.Integer, nullable=False, default=5)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"))

    categoria = db.relationship("Categoria", back_populates="productos")
    proveedor = db.relationship("Proveedor", back_populates="productos")

    def to_dict(self):
        return {
            "id": self.id,
            "codigo_barras": self.codigo_barras,
            "nombre": self.nombre,
            "unidad": self.unidad,
            "precio_compra": float(self.precio_compra),
            "precio_venta": float(self.precio_venta),
            "stock_actual": self.stock_actual,
            "stock_minimo": self.stock_minimo,
            "activo": self.activo,
            "categoria": self.categoria.nombre if self.categoria else None,
            "proveedor": self.proveedor.nombre if self.proveedor else None,
        }
