# Inventario Gastrobar — Persistencia Políglota (MySQL + MongoDB)

Proyecto del curso **Nuevas Tecnologías de Desarrollo** — Entrega 2: Integración de datos no estructurados (NoSQL).
Autor: Juan Esteban Pico Briceño

API en Flask para manejar el inventario de un gastrobar. La aplicación usa **dos bases de datos al mismo tiempo**:

| Base | Qué guarda | Por qué |
|---|---|---|
| **MySQL** (SQL) | categorías, proveedores, productos y el stock oficial | Son datos con estructura fija, que se relacionan entre sí y necesitan integridad (llaves foráneas, valores únicos). |
| **MongoDB** (NoSQL) | movimientos de inventario, fichas de producto y logs de actividad | Son muchos registros (cada venta es un movimiento), y cada uno trae información diferente según el tipo. |

La justificación completa está en el PDF de la entrega (`docs/Entrega2_NoSQL_Justificacion.pdf`).

---

## 1. Estructura del proyecto

```
inventario-gastrobar/
├── app.py              # arranca Flask y conecta las dos bases
├── config.py           # lee las conexiones desde .env
├── extensions.py       # objetos de conexión: db (MySQL) y mongo (MongoDB) + índices
├── models.py           # tablas SQL: Categoria, Proveedor, Producto
├── utils.py            # ayudas: convertir documentos a JSON, registrar logs
├── routes/
│   ├── categorias.py   # CRUD MySQL
│   ├── proveedores.py  # CRUD MySQL
│   ├── productos.py    # CRUD MySQL + endpoint combinado /detalle
│   ├── fichas.py       # CRUD MongoDB (atributos variables)
│   ├── movimientos.py  # CRUD MongoDB + lógica que actualiza stock en MySQL
│   └── reportes.py     # reportes que combinan las dos bases + logs
├── sql/schema.sql      # script de las tablas (referencia)
├── scripts/
│   ├── seed.py         # llena las dos bases con datos de prueba
│   └── probar_api.py   # prueba todos los endpoints y guarda la salida
└── docs/evidencias/    # salidas y capturas de ejecución
```

## 2. Instalación y ejecución

Requisitos: Python 3.10+, MySQL (o XAMPP) y MongoDB (local o Atlas).

```bash
# 1. clonar
git clone https://github.com/MrHuesitozzz/inventario-gastrobar.git
cd inventario-gastrobar

# 2. entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 3. dependencias
pip install -r requirements.txt

# 4. crear la base en MySQL (solo la base, las tablas las crea la app)
#    En MySQL Workbench / phpMyAdmin:
#    CREATE DATABASE inventario_gastrobar;

# 5. configurar conexiones
copy .env.example .env         # Windows  (cp en Linux/Mac)
#    y editar .env con el usuario/clave de MySQL y la URI de Mongo

# 6. datos de prueba (borra y vuelve a crear todo)
python scripts/seed.py

# 7. correr
python app.py
```

La API queda en `http://127.0.0.1:5000`. Para revisar que las dos bases estén conectadas: `GET /api/salud`.

> Si no se tiene MongoDB instalado se puede poner `MONGO_URI=mongomock://` en el `.env`. Eso usa un Mongo simulado en memoria (sirve para probar, pero los datos se pierden al apagar la app).

## 3. Endpoints

### MySQL (datos estructurados)
| Método | Ruta | Qué hace |
|---|---|---|
| GET / POST | `/api/categorias` | listar / crear |
| GET / PUT / DELETE | `/api/categorias/<id>` | ver / editar / borrar |
| GET / POST | `/api/proveedores` | listar / crear |
| GET / PUT / DELETE | `/api/proveedores/<id>` | ver / editar / borrar |
| GET / POST | `/api/productos` | listar (`?categoria_id=`) / crear |
| GET / PUT / DELETE | `/api/productos/<id>` | ver / editar / borrar (también borra la ficha en Mongo) |

### MongoDB (datos dinámicos)
| Método | Ruta | Qué hace |
|---|---|---|
| GET / POST | `/api/fichas` | listar (`?tipo=`, `?etiqueta=`) / crear ficha de un producto |
| GET / PUT / DELETE | `/api/fichas/<producto_id>` | ver / agregar o cambiar atributos / borrar |
| GET / POST | `/api/movimientos` | listar (`?producto_id=&tipo=&dias=&limite=`) / registrar entrada, salida, merma o ajuste |
| GET / PUT / DELETE | `/api/movimientos/<id>` | ver / corregir motivo o detalle / anular (revierte el stock) |
| GET | `/api/logs` | últimos registros de actividad (`?entidad=&accion=&limite=`) |

### ⭐ Combinan SQL + NoSQL
| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/api/productos/<id>/detalle` | Producto, categoría y proveedor (**MySQL**) + ficha y **últimos 10 movimientos** (**MongoDB**) |
| POST | `/api/movimientos` | Valida el producto y el stock en **MySQL**, guarda el movimiento en **MongoDB** y actualiza el stock en **MySQL**. Si Mongo falla, se hace rollback en MySQL. |
| GET | `/api/reportes/stock-bajo?dias=7` | Productos bajo el mínimo (**MySQL**) + consumo de los últimos días calculado con aggregation (**MongoDB**) → días estimados que alcanza el stock |
| GET | `/api/reportes/mas-vendidos?dias=30&top=5` | Ranking de salidas (**MongoDB**) + nombre, categoría y precio para estimar ingresos (**MySQL**) |

## 4. Cómo se conectan las dos bases

La unión entre los dos mundos es el campo **`producto_id`**: es el `id` de la tabla `productos` en MySQL y se guarda dentro de cada documento de Mongo.

```
MySQL: productos.id = 1  ─────────┐
                                   ├── fichas_producto.producto_id = 1
                                   └── movimientos_inventario.producto_id = 1  (muchos)
```

Flujo al registrar una venta (`POST /api/movimientos` con tipo `salida`):

1. Busca el producto en MySQL y revisa que esté activo.
2. Calcula el nuevo stock; si queda negativo responde `409`.
3. Cambia el stock en MySQL **sin confirmar** todavía.
4. Inserta el movimiento en MongoDB.
5. Si Mongo respondió bien → `commit` en MySQL. Si falló → `rollback`, el stock queda como estaba.
6. Escribe un log en `logs_actividad`.

### Ejemplos de documentos en MongoDB

`fichas_producto` (cada producto con atributos distintos):
```json
{ "producto_id": 1, "tipo": "cerveza",
  "atributos": { "grados_alcohol": 4.7, "volumen_ml": 330, "estilo": "lager", "retornable": true },
  "etiquetas": ["nacional", "mas_pedida"] }

{ "producto_id": 8, "tipo": "comida",
  "atributos": { "requiere_refrigeracion": true, "vida_util_dias": 15, "alergenos": ["soya"], "peso_g": 1000 } }
```

`movimientos_inventario` (el `detalle` cambia según el tipo):
```json
{ "producto_id": 1, "producto_nombre": "Cerveza Club Colombia Dorada 330ml",
  "tipo": "salida", "cantidad": 3, "stock_anterior": 123, "stock_resultante": 120,
  "usuario": "mesero1", "detalle": { "mesa": 9, "comanda": 2662 }, "fecha": "2026-11-03T02:08:36" }

{ "producto_id": 1, "tipo": "entrada", "cantidad": 140,
  "detalle": { "factura_proveedor": "FV-512", "lote": "L4471" }, "motivo": "Pedido semanal", ... }
```

Índices creados al iniciar la app (`extensions.py`):
- `movimientos_inventario`: `{producto_id: 1, fecha: -1}` → hace rápido "últimos N movimientos de un producto".
- `fichas_producto`: `{producto_id: 1}` único → un producto solo tiene una ficha.
- `logs_actividad`: `{fecha: -1}`.

## 5. Evidencias de ejecución

**Prueba automática:** `python scripts/probar_api.py` llena las bases y llama 20 endpoints (CRUD de las dos bases, validaciones y endpoints combinados). La salida completa, con lo que se envió y lo que respondió cada uno, está en [`docs/evidencias/salida_pruebas.md`](docs/evidencias/salida_pruebas.md).

Resumen de esa ejecución:

| # | Petición | Resultado |
|---|---|---|
| 1 | `GET /api/salud` | 200 – mysql: conectado, mongodb: conectado |
| 3 | `POST /api/productos` (Ron Viejo de Caldas, stock 4) | 201 |
| 6 | `POST /api/fichas` con atributos de licor | 201 |
| 7 | `PUT /api/fichas/10` agregando `sabor` | 200 – atributo nuevo sin tocar tablas |
| 9 | `POST /api/movimientos` entrada de 12 | 201 – stock 4 → 16 |
| 10 | `POST /api/movimientos` salida de 3 (mesa 4) | 201 – stock 16 → 13 |
| 11 | `POST /api/movimientos` salida de 500 | 409 – "Stock insuficiente. Hay 13 botella(s)" |
| 13 | `DELETE /api/movimientos/<id>` (anular la entrada) | 200 – stock revertido a 1 |
| 15 | `GET /api/productos/1/detalle` | 200 – producto (MySQL) + ficha + 10 movimientos (MongoDB) |
| 16 | `GET /api/reportes/stock-bajo?dias=7` | 200 – productos en alerta con días estimados |
| 17 | `GET /api/reportes/mas-vendidos` | 200 – top 5 con ingreso estimado |
| 19 | `DELETE /api/productos/10` | 200 – se borra en MySQL y su ficha en MongoDB |

También se probó que si MongoDB falla al guardar un movimiento la API responde 500 y el stock en MySQL **no cambia** (rollback).

**Capturas:**

<!-- Reemplazar con capturas propias -->
- `docs/evidencias/01_salud.png` – Postman, GET /api/salud
- `docs/evidencias/02_detalle.png` – Postman, GET /api/productos/1/detalle
- `docs/evidencias/03_mongo_compass.png` – colecciones en MongoDB Compass
- `docs/evidencias/04_mysql.png` – tablas en MySQL Workbench / phpMyAdmin

## 6. Tecnologías

Python 3 · Flask 3 · Flask-SQLAlchemy · PyMySQL · MySQL · PyMongo · MongoDB · python-dotenv
