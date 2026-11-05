"""
Llena las dos bases con datos de prueba.
    python scripts/seed.py

OJO: borra lo que haya y vuelve a crear todo.
"""
import os
import sys
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extensions import db, mongo  # noqa: E402
from models import Categoria, Proveedor, Producto  # noqa: E402

CATEGORIAS = [
    ("Cervezas", "Nacionales e importadas"),
    ("Licores", "Aguardiente, ron, whisky"),
    ("Bebidas sin alcohol", "Gaseosas, agua, jugos"),
    ("Comidas", "Insumos de cocina y snacks"),
    ("Desechables", "Vasos, servilletas, pitillos"),
]

PROVEEDORES = [
    ("Bavaria S.A.", "860005224-6", "6013099000", "pedidos@bavaria.com.co"),
    ("Distribuidora La 80", "901234567-1", "3104567890", "ventas@la80.com"),
    ("Postobón", "890903939-8", "6015760000", "clientes@postobon.com"),
    ("Surtidor Plaza Paloquemao", "79845123-2", "3001234567", None),
]

# (codigo, nombre, unidad, compra, venta, stock, minimo, categoria, proveedor, ficha)
PRODUCTOS = [
    ("7702004001", "Cerveza Club Colombia Dorada 330ml", "botella", 2500, 6000, 120, 48, 1, 1,
     {"tipo": "cerveza", "atributos": {"grados_alcohol": 4.7, "volumen_ml": 330, "estilo": "lager",
                                        "retornable": True}, "etiquetas": ["nacional", "mas_pedida"]}),
    ("7702004002", "Cerveza Corona 355ml", "botella", 3800, 9000, 30, 24, 1, 2,
     {"tipo": "cerveza", "atributos": {"grados_alcohol": 4.5, "volumen_ml": 355, "estilo": "pilsner",
                                        "retornable": False, "pais_origen": "México"},
      "etiquetas": ["importada"]}),
    ("7702049001", "Aguardiente Antioqueño Tapa Azul 750ml", "botella", 38000, 85000, 6, 5, 2, 2,
     {"tipo": "licor", "atributos": {"grados_alcohol": 24, "volumen_ml": 750, "sin_azucar": True,
                                      "se_vende_por_trago": True, "tragos_por_botella": 25},
      "etiquetas": ["nacional"]}),
    ("5000267014", "Whisky Johnnie Walker Red 700ml", "botella", 65000, 160000, 3, 2, 2, 2,
     {"tipo": "licor", "atributos": {"grados_alcohol": 40, "volumen_ml": 700, "pais_origen": "Escocia",
                                      "anos_anejamiento": None}, "etiquetas": ["importado", "premium"]}),
    ("7702090001", "Coca-Cola 400ml", "botella", 1900, 4500, 60, 24, 3, 3,
     {"tipo": "bebida", "atributos": {"volumen_ml": 400, "azucar": True, "retornable": False}}),
    ("7702090002", "Agua Cristal 600ml", "botella", 1000, 3000, 15, 20, 3, 3,
     {"tipo": "bebida", "atributos": {"volumen_ml": 600, "con_gas": False}}),
    ("2000000001", "Papa criolla (kg)", "kg", 3500, 0, 8, 5, 4, 4,
     {"tipo": "comida", "atributos": {"requiere_refrigeracion": False, "vida_util_dias": 10,
                                       "se_usa_en": ["picada", "salchipapa"]}}),
    ("2000000002", "Chorizo santarrosano x10", "paquete", 18000, 0, 4, 3, 4, 4,
     {"tipo": "comida", "atributos": {"requiere_refrigeracion": True, "vida_util_dias": 15,
                                       "alergenos": ["soya"], "peso_g": 1000}}),
    ("2000000003", "Vasos plásticos 7oz x50", "paquete", 4500, 0, 10, 4, 5, 4,
     {"tipo": "desechable", "atributos": {"material": "polipropileno", "unidades_por_paquete": 50,
                                           "biodegradable": False}}),
]

USUARIOS = ["jhon", "mesero1", "mesero2"]

# consumo diario (min, max) y pedido semanal (min, max) por código de barras
RITMO = {
    "7702004001": {"consumo": (10, 30), "pedido": (120, 150)},  # Club Colombia
    "7702004002": {"consumo": (2, 8), "pedido": (35, 45)},      # Corona
    "7702049001": {"consumo": (0, 2), "pedido": (7, 9)},        # Aguardiente
    "5000267014": {"consumo": (0, 1), "pedido": (3, 5)},        # Whisky
    "7702090001": {"consumo": (3, 10), "pedido": (48, 55)},     # Coca-Cola
    "7702090002": {"consumo": (2, 6), "pedido": (24, 24)},      # Agua
    "2000000001": {"consumo": (1, 2), "pedido": (11, 13)},       # Papa criolla
    "2000000002": {"consumo": (0, 1), "pedido": (4, 5)},        # Chorizo
    "2000000003": {"consumo": (0, 2), "pedido": (7, 9)},        # Vasos
}


def sembrar():
    # ---------- MySQL ----------
    db.drop_all()
    db.create_all()
    for n, d in CATEGORIAS:
        db.session.add(Categoria(nombre=n, descripcion=d))
    for n, nit, tel, mail in PROVEEDORES:
        db.session.add(Proveedor(nombre=n, nit=nit, telefono=tel, email=mail))
    db.session.flush()

    productos = []
    for cod, nom, uni, pc, pv, stock, minimo, cat, prov, ficha in PRODUCTOS:
        p = Producto(codigo_barras=cod, nombre=nom, unidad=uni, precio_compra=pc, precio_venta=pv,
                     stock_actual=stock, stock_minimo=minimo, categoria_id=cat, proveedor_id=prov)
        db.session.add(p)
        productos.append((p, ficha))
    db.session.commit()

    # ---------- MongoDB ----------
    mongo.fichas.delete_many({})
    mongo.movimientos.delete_many({})
    mongo.logs.delete_many({})

    for p, ficha in productos:
        mongo.fichas.insert_one({"producto_id": p.id, "notas": None, "etiquetas": [],
                                 "actualizado": datetime.utcnow(), **ficha})

    # Historial de 30 días simulado hacia adelante:
    # cada producto tiene su propio consumo diario y su pedido semanal.
    random.seed(7)
    ahora = datetime.utcnow()
    for p, _ in productos:
        lo, hi = RITMO[p.codigo_barras]["consumo"]
        rlo, rhi = RITMO[p.codigo_barras]["pedido"]
        stock = p.stock_actual
        docs = []

        def mov(tipo, cant, fecha, detalle, motivo):
            nonlocal stock
            anterior = stock
            stock += cant if tipo == "entrada" else -cant
            docs.append({"producto_id": p.id, "producto_nombre": p.nombre, "tipo": tipo,
                         "cantidad": cant, "stock_anterior": anterior, "stock_resultante": stock,
                         "usuario": random.choice(USUARIOS), "motivo": motivo,
                         "detalle": detalle, "fecha": fecha})

        for dia in range(30, 0, -1):
            base = ahora - timedelta(days=dia)
            if dia % 7 == 0:  # llega el pedido semanal en la mañana
                mov("entrada", random.randint(rlo, rhi), base.replace(hour=14),
                    {"factura_proveedor": f"FV-{random.randint(100, 999)}",
                     "lote": f"L{random.randint(1000, 9999)}"}, "Pedido semanal")
            vendido = min(random.randint(lo, hi), stock)
            if vendido > 0:
                detalle = ({"mesa": random.randint(1, 12), "comanda": random.randint(1000, 9999)}
                           if p.categoria_id in (1, 2, 3) else {"preparacion": "cocina"})
                mov("salida", vendido, base.replace(hour=random.randint(19, 23)), detalle, None)
            if stock > 0 and random.random() < 0.05:
                mov("merma", 1, base.replace(hour=23, minute=50), {"causa": random.choice(
                    ["botella rota", "producto vencido", "derrame"])}, "Pérdida")
        if docs:
            mongo.movimientos.insert_many(docs)
        p.stock_actual = stock  # MySQL queda con el stock final de la simulación
    db.session.commit()

    print(f"MySQL  -> {Categoria.query.count()} categorías, {Proveedor.query.count()} proveedores, "
          f"{Producto.query.count()} productos")
    print(f"Mongo  -> {mongo.fichas.count_documents({})} fichas, "
          f"{mongo.movimientos.count_documents({})} movimientos")


if __name__ == "__main__":
    from app import app
    with app.app_context():
        sembrar()
