"""
Prueba automática de la API: llena datos y llama los endpoints principales.
Guarda lo que respondió cada uno en docs/evidencias/salida_pruebas.md

    python scripts/probar_api.py
"""
import os
import sys
import json

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from app import app  # noqa: E402
from scripts.seed import sembrar  # noqa: E402

salida = ["# Evidencias de ejecución (salida automática)\n"]


def llamar(metodo, url, body=None, titulo="", recortar=None):
    cliente = app.test_client()
    r = getattr(cliente, metodo.lower())(url, json=body)
    datos = r.get_json()
    mostrar = datos
    if recortar and isinstance(datos, list):
        mostrar = datos[:recortar]
    print(f"{metodo} {url} -> {r.status_code}")
    salida.append(f"\n## {titulo}\n\n`{metodo} {url}` → **{r.status_code}**\n")
    if body is not None:
        salida.append("\nBody enviado:\n```json\n" + json.dumps(body, ensure_ascii=False, indent=2) + "\n```\n")
    salida.append("\nRespuesta:\n```json\n" + json.dumps(mostrar, ensure_ascii=False, indent=2) + "\n```\n")
    return r.status_code, datos


with app.app_context():
    sembrar()

llamar("GET", "/api/salud", titulo="1. Conexión a las dos bases")

# --- CRUD SQL ---
_, cat = llamar("POST", "/api/categorias", {"nombre": "Cócteles", "descripcion": "Preparados en barra"},
                titulo="2. CREATE categoría (MySQL)")
_, prod = llamar("POST", "/api/productos", {
    "codigo_barras": "7700000999", "nombre": "Ron Viejo de Caldas 750ml", "unidad": "botella",
    "precio_compra": 42000, "precio_venta": 95000, "stock_actual": 4, "stock_minimo": 3,
    "categoria_id": 2, "proveedor_id": 2}, titulo="3. CREATE producto (MySQL)")
pid = prod["id"]
llamar("GET", "/api/productos?categoria_id=2", titulo="4. READ productos de la categoría Licores (MySQL)")
llamar("PUT", f"/api/productos/{pid}", {"precio_venta": 98000}, titulo="5. UPDATE precio (MySQL)")

# --- CRUD NoSQL: fichas ---
llamar("POST", "/api/fichas", {"producto_id": pid, "tipo": "licor",
       "atributos": {"grados_alcohol": 35, "volumen_ml": 750, "anos_anejamiento": 3},
       "etiquetas": ["nacional"]}, titulo="6. CREATE ficha con atributos variables (MongoDB)")
llamar("PUT", f"/api/fichas/{pid}", {"atributos": {"sabor": "tradicional"}},
       titulo="7. UPDATE ficha: se agrega un atributo nuevo sin cambiar ninguna tabla (MongoDB)")
llamar("GET", "/api/fichas?tipo=cerveza", titulo="8. READ fichas filtradas por tipo (MongoDB)")

# --- Movimientos (lógica SQL + NoSQL) ---
_, mov = llamar("POST", "/api/movimientos", {"producto_id": pid, "tipo": "entrada", "cantidad": 12,
                "usuario": "jhon", "motivo": "Pedido semanal",
                "detalle": {"factura_proveedor": "FV-2231", "lote": "L5521"}},
                titulo="9. CREATE movimiento de ENTRADA: guarda en Mongo y sube stock en MySQL")
_, mov2 = llamar("POST", "/api/movimientos", {"producto_id": pid, "tipo": "salida", "cantidad": 3,
                 "usuario": "mesero1", "detalle": {"mesa": 4, "comanda": 5120}},
                 titulo="10. CREATE movimiento de SALIDA con detalle distinto (mesa/comanda)")
llamar("POST", "/api/movimientos", {"producto_id": pid, "tipo": "salida", "cantidad": 500},
       titulo="11. Validación: salida mayor al stock (debe fallar)")
llamar("PUT", f"/api/movimientos/{mov2['_id']}", {"motivo": "Venta mesa 4 - cumpleaños"},
       titulo="12. UPDATE movimiento (MongoDB)")
llamar("DELETE", f"/api/movimientos/{mov['_id']}",
       titulo="13. DELETE (anular) movimiento: se borra de Mongo y se revierte stock en MySQL")
llamar("GET", f"/api/productos/{pid}", titulo="14. Stock en MySQL después de anular")

# --- Endpoints combinados ---
llamar("GET", "/api/productos/1/detalle",
       titulo="15. ⭐ ENDPOINT COMBINADO: producto (MySQL) + ficha y últimos 10 movimientos (MongoDB)")
llamar("GET", "/api/reportes/stock-bajo?dias=7",
       titulo="16. ⭐ REPORTE COMBINADO: stock bajo (MySQL) + consumo de 7 días (MongoDB)")
llamar("GET", "/api/reportes/mas-vendidos?dias=30&top=5",
       titulo="17. ⭐ REPORTE COMBINADO: más vendidos (MongoDB) + precios (MySQL)")
llamar("GET", "/api/logs?limite=5", titulo="18. Logs de actividad (MongoDB)")

# --- DELETE SQL ---
llamar("DELETE", f"/api/productos/{pid}", titulo="19. DELETE producto (MySQL) y su ficha (MongoDB)")
llamar("DELETE", f"/api/categorias/{cat['id']}", titulo="20. DELETE categoría (MySQL)")

ruta = os.path.join(RAIZ, "docs", "evidencias", "salida_pruebas.md")
with open(ruta, "w", encoding="utf-8") as f:
    f.write("".join(salida))
print("\nResultado guardado en", ruta)
