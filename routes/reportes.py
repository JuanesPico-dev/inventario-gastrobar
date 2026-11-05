"""
Reportes que COMBINAN MySQL + MongoDB, y consulta de logs.
"""
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from pymongo import DESCENDING
from extensions import db, mongo
from models import Producto
from utils import doc_a_json

bp = Blueprint("reportes", __name__, url_prefix="/api")


@bp.get("/reportes/stock-bajo")
def stock_bajo():
    """
    Productos con stock <= stock_minimo (MySQL) + cuánto se ha consumido
    en los últimos N días (MongoDB). Con eso se estima para cuántos días alcanza.
    """
    dias = request.args.get("dias", 7, type=int)
    desde = datetime.utcnow() - timedelta(days=dias)

    # 1) MySQL: productos en alerta
    criticos = Producto.query.filter(
        Producto.activo.is_(True), Producto.stock_actual <= Producto.stock_minimo
    ).all()
    ids = [p.id for p in criticos]

    # 2) MongoDB: suma de salidas por producto (aggregation pipeline)
    pipeline = [
        {"$match": {"producto_id": {"$in": ids}, "tipo": "salida", "fecha": {"$gte": desde}}},
        {"$group": {"_id": "$producto_id", "consumido": {"$sum": "$cantidad"}}},
    ]
    consumo = {r["_id"]: r["consumido"] for r in mongo.movimientos.aggregate(pipeline)}

    # 3) unimos
    resultado = []
    for p in criticos:
        consumido = consumo.get(p.id, 0)
        promedio_dia = round(consumido / dias, 2)
        resultado.append({
            "producto_id": p.id,
            "nombre": p.nombre,
            "proveedor": p.proveedor.nombre if p.proveedor else None,
            "stock_actual": p.stock_actual,
            "stock_minimo": p.stock_minimo,
            f"consumo_ultimos_{dias}_dias": consumido,
            "consumo_promedio_dia": promedio_dia,
            "dias_estimados_restantes": round(p.stock_actual / promedio_dia, 1) if promedio_dia else None,
        })
    resultado.sort(key=lambda r: (r["dias_estimados_restantes"] is None, r["dias_estimados_restantes"]))
    return jsonify({"periodo_dias": dias, "total": len(resultado), "productos": resultado})


@bp.get("/reportes/mas-vendidos")
def mas_vendidos():
    """Top de productos por salidas (MongoDB) enriquecido con precio de venta (MySQL)."""
    dias = request.args.get("dias", 30, type=int)
    top = request.args.get("top", 5, type=int)
    desde = datetime.utcnow() - timedelta(days=dias)

    pipeline = [
        {"$match": {"tipo": "salida", "fecha": {"$gte": desde}}},
        {"$group": {"_id": "$producto_id", "unidades": {"$sum": "$cantidad"},
                    "num_salidas": {"$sum": 1}}},
        {"$sort": {"unidades": -1}},
        {"$limit": top},
    ]
    filas = list(mongo.movimientos.aggregate(pipeline))
    productos = {p.id: p for p in Producto.query.filter(Producto.id.in_([f["_id"] for f in filas]))}

    salida = []
    for f in filas:
        p = productos.get(f["_id"])
        salida.append({
            "producto_id": f["_id"],
            "nombre": p.nombre if p else "(producto eliminado)",
            "categoria": p.categoria.nombre if p else None,
            "unidades_vendidas": f["unidades"],
            "numero_salidas": f["num_salidas"],
            "ingreso_estimado": float(p.precio_venta) * f["unidades"] if p else None,
        })
    return jsonify({"periodo_dias": dias, "top": salida})


@bp.get("/logs")
def logs():
    """Últimos registros de actividad. ?entidad=producto&accion=CREAR&limite=20"""
    filtro = {k: request.args[k] for k in ("entidad", "accion", "usuario") if request.args.get(k)}
    limite = request.args.get("limite", 20, type=int)
    docs = mongo.logs.find(filtro).sort("fecha", DESCENDING).limit(limite)
    return jsonify([doc_a_json(d) for d in docs])
