# Inventario Gastrobar — API con MySQL + MongoDB + JWT

Proyecto del curso **Nuevas Tecnologías de Desarrollo** — Konrad Lorenz
Autor: Juan Esteban Pico Briceño

API en Flask para manejar el inventario de un gastrobar: productos, proveedores, ventas, entradas de mercancía, pérdidas y reportes. Se construyó en tres entregas:

| Entrega | Qué se agregó |
|---|---|
| 1 | Estructura SQL (MySQL): categorías, proveedores y productos con su CRUD |
| 2 | MongoDB para datos no estructurados: movimientos de inventario, fichas con atributos variables y logs (persistencia políglota) |
| **3** | **Seguridad**: registro y login con contraseñas hasheadas, tokens JWT y roles (admin / empleado) |

---

## 1. Tecnologías

Python 3 · Flask 3 · Flask-SQLAlchemy · PyMySQL · **MySQL 8** · PyMongo · **MongoDB** · **Flask-JWT-Extended** · Werkzeug (hashing) · python-dotenv · Postman

| Base | Qué guarda |
|---|---|
| MySQL | `categorias`, `proveedores`, `productos` (con el stock oficial) y `usuarios` |
| MongoDB | `movimientos_inventario`, `fichas_producto`, `logs_actividad` |

## 2. Estructura del proyecto

```
inventario-gastrobar/
├── app.py              # arranca Flask, conecta MySQL, MongoDB y JWT
├── config.py           # lee la configuración desde .env
├── extensions.py       # conexiones: db (MySQL), mongo (MongoDB), jwt
├── models.py           # tablas SQL: Categoria, Proveedor, Producto, Usuario
├── seguridad.py        # decorador @rol_requerido (control de acceso por rol)
├── utils.py            # ayudas: respuestas de error, logs en Mongo
├── routes/
│   ├── auth.py         # registro, login, perfil
│   ├── usuarios.py     # gestión de usuarios (solo admin)
│   ├── categorias.py   # CRUD MySQL
│   ├── proveedores.py  # CRUD MySQL
│   ├── productos.py    # CRUD MySQL + detalle combinado SQL/NoSQL
│   ├── fichas.py       # CRUD MongoDB
│   ├── movimientos.py  # ventas, entradas, mermas (MongoDB + stock en MySQL)
│   └── reportes.py     # reportes combinados + logs
├── scripts/
│   ├── seed.py         # datos de prueba (BORRA y recrea todo)
│   ├── crear_admin.py  # crea el primer administrador
│   └── probar_api.py   # prueba automática de los endpoints
├── sql/schema.sql
└── docs/evidencias/    # capturas de ejecución
```

## 3. Cómo ejecutarlo

**Requisitos:** Python 3.10+, MySQL 8 (o XAMPP), MongoDB Community Server, Git y Postman.

```bash
# 1. Clonar e instalar
git clone https://github.com/JuanesPico-dev/inventario-gastrobar.git
cd inventario-gastrobar
python -m venv venv
venv\Scripts\activate              # Windows  (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt

# 2. Crear la base en MySQL (DBeaver, Workbench o phpMyAdmin)
#    CREATE DATABASE inventario_gastrobar;

# 3. Configuración
copy .env.example .env             # Linux/Mac: cp .env.example .env
#    editar .env con la clave de MySQL y una JWT_SECRET_KEY propia

# 4. Datos de prueba (opcional; borra todo, incluidos los usuarios)
python scripts/seed.py

# 5. Crear el primer administrador
python scripts/crear_admin.py

# 6. Arrancar
python app.py                      # -> http://127.0.0.1:5000
```

Revisar que las dos bases estén conectadas: `GET http://127.0.0.1:5000/api/salud`

Variables del `.env`:

| Variable | Ejemplo | Para qué |
|---|---|---|
| `SQL_URI` | `mysql+pymysql://root:clave@localhost:3306/inventario_gastrobar` | conexión MySQL |
| `MONGO_URI` | `mongodb://localhost:27017` | conexión MongoDB (`mongomock://` para pruebas sin Mongo) |
| `MONGO_DB` | `inventario_gastrobar` | nombre de la base en Mongo |
| `JWT_SECRET_KEY` | texto largo y aleatorio | firma de los tokens. **Nunca se sube a GitHub** |

> Si DBeaver muestra *"Public Key Retrieval is not allowed"*: en Driver properties poner `allowPublicKeyRetrieval=true` y `useSSL=false`.

---

## 4. Seguridad (Entrega 3)

### 4.1 Autenticación con contraseñas hasheadas

- Las contraseñas **nunca** se guardan en texto plano. Se usa `generate_password_hash` de Werkzeug (algoritmo **scrypt** con **salt** aleatorio), y en el login se compara con `check_password_hash`.
- El hash queda así en la tabla `usuarios`: `scrypt:32768:8:1$<salt>$<hash>`. El salt hace que dos usuarios con la misma clave tengan hashes distintos.
- `password_hash` nunca se devuelve en las respuestas de la API.
- Contraseña mínima de 8 caracteres y email único.
- Ante un login fallido el mensaje siempre es *"Credenciales inválidas"*, sin decir si el email existe o no.

### 4.2 Autorización con JWT

1. `POST /api/auth/login` devuelve un `access_token` (JWT) firmado con `JWT_SECRET_KEY`.
2. Las rutas protegidas exigen el header `Authorization: Bearer <token>`.
3. El token dura **8 horas** (un turno). Después toca volver a iniciar sesión.
4. Si alguien modifica el token (por ejemplo para cambiarse el rol), la firma deja de coincidir y se rechaza.

### 4.3 Roles y permisos (RBAC)

Hay dos roles:
- **admin** → dueño o administrador del gastrobar
- **empleado** → mesero o barra

Todo usuario que se registra queda como **empleado**. El rol **no** se recibe en el registro; solo un admin puede cambiarlo. El primer admin se crea con `scripts/crear_admin.py`.

El control se hace con el decorador `@rol_requerido` (`seguridad.py`), que en cada petición:
1. Verifica que venga un token válido → si no, **401**.
2. Busca al usuario en MySQL y revisa que siga **activo** → si fue desactivado, **401** aunque su token no haya vencido.
3. Revisa que tenga el rol que pide la ruta → si no, **403**.

```python
@bp.post("")
@rol_requerido("admin")   # solo administradores
def crear():
    ...
```

**Matriz de permisos:**

| Acción | Admin | Empleado |
|---|:---:|:---:|
| Ver productos, categorías, proveedores, fichas, detalle de producto | ✅ | ✅ |
| Crear / editar / borrar productos, categorías, proveedores, fichas | ✅ | ❌ |
| Registrar **salida** (venta) y **merma** (pérdida) | ✅ | ✅ |
| Registrar **entrada** (llegada de pedido) y **ajuste** | ✅ | ❌ |
| Corregir o anular movimientos | ✅ | ❌ |
| Ver reportes (stock bajo, más vendidos) y logs | ✅ | ❌ |
| Gestionar usuarios (listar, cambiar rol, activar/desactivar) | ✅ | ❌ |

El usuario que queda registrado en cada movimiento y en cada log **sale del token**, no del body, así que nadie puede registrar una venta a nombre de otro.

**Códigos de respuesta:** `401` = no sé quién eres (sin token, token inválido o usuario inactivo) · `403` = sé quién eres pero no tienes permiso.

---

## 5. Documentación de la API

Base URL: `http://127.0.0.1:5000`
🔓 = público · 👤 = cualquier usuario con token · 👑 = solo admin

### Autenticación
| Método | Ruta | Acceso | Body | Respuesta |
|---|---|:---:|---|---|
| POST | `/api/auth/registro` | 🔓 | `{"nombre", "email", "password"}` | 201 usuario creado como empleado · 400 datos inválidos · 409 email repetido |
| POST | `/api/auth/login` | 🔓 | `{"email", "password"}` | 200 `{"access_token", "usuario"}` · 401 credenciales inválidas · 403 usuario inactivo |
| GET | `/api/auth/yo` | 👤 | — | 200 datos del usuario dueño del token |

### Usuarios
| Método | Ruta | Acceso | Body | Respuesta |
|---|---|:---:|---|---|
| GET | `/api/usuarios` | 👑 | — | 200 lista de usuarios |
| PUT | `/api/usuarios/<id>` | 👑 | `{"rol": "admin"\|"empleado"}` y/o `{"activo": true\|false}` | 200 · 404 · 409 si el admin intenta cambiarse a sí mismo |

### Categorías y proveedores (MySQL)
| Método | Ruta | Acceso |
|---|---|:---:|
| GET | `/api/categorias` · `/api/categorias/<id>` | 👤 |
| POST / PUT / DELETE | `/api/categorias` · `/api/categorias/<id>` | 👑 |
| GET | `/api/proveedores` · `/api/proveedores/<id>` | 👤 |
| POST / PUT / DELETE | `/api/proveedores` · `/api/proveedores/<id>` | 👑 |

Body categoría: `{"nombre", "descripcion"}` · Body proveedor: `{"nombre", "nit", "telefono", "email"}`

### Productos (MySQL)
| Método | Ruta | Acceso | Notas |
|---|---|:---:|---|
| GET | `/api/productos?categoria_id=` | 👤 | lista, filtro opcional |
| GET | `/api/productos/<id>` | 👤 | |
| GET | `/api/productos/<id>/detalle?limite=10` | 👤 | ⭐ producto (MySQL) + ficha y últimos movimientos (MongoDB) |
| POST | `/api/productos` | 👑 | `{"nombre", "categoria_id", "codigo_barras", "unidad", "precio_compra", "precio_venta", "stock_actual", "stock_minimo", "proveedor_id"}` |
| PUT | `/api/productos/<id>` | 👑 | el stock no se edita aquí, solo con movimientos |
| DELETE | `/api/productos/<id>` | 👑 | también borra su ficha en Mongo |

### Fichas de producto (MongoDB)
| Método | Ruta | Acceso | Notas |
|---|---|:---:|---|
| GET | `/api/fichas?tipo=&etiqueta=` | 👤 | |
| GET | `/api/fichas/<producto_id>` | 👤 | |
| POST | `/api/fichas` | 👑 | `{"producto_id", "tipo", "atributos": {...}, "etiquetas": [...]}` |
| PUT | `/api/fichas/<producto_id>` | 👑 | agrega o cambia atributos sin borrar los demás |
| DELETE | `/api/fichas/<producto_id>` | 👑 | |

### Movimientos de inventario (MongoDB + stock en MySQL)
| Método | Ruta | Acceso | Notas |
|---|---|:---:|---|
| GET | `/api/movimientos?producto_id=&tipo=&dias=&limite=` | 👤 | |
| GET | `/api/movimientos/<id>` | 👤 | |
| POST | `/api/movimientos` | 👤 | `{"producto_id", "tipo", "cantidad", "motivo", "detalle": {...}}`. El empleado solo puede `salida` y `merma`; el admin también `entrada` y `ajuste`. 409 si no alcanza el stock |
| PUT | `/api/movimientos/<id>` | 👑 | solo `motivo` y `detalle` |
| DELETE | `/api/movimientos/<id>` | 👑 | anula el movimiento y revierte el stock en MySQL |

### Reportes y logs
| Método | Ruta | Acceso | Notas |
|---|---|:---:|---|
| GET | `/api/reportes/stock-bajo?dias=7` | 👑 | ⭐ productos bajo el mínimo (MySQL) + consumo y días estimados (MongoDB) |
| GET | `/api/reportes/mas-vendidos?dias=30&top=5` | 👑 | ⭐ ranking de ventas (MongoDB) + precios (MySQL) |
| GET | `/api/logs?entidad=&accion=&usuario=&limite=` | 👑 | actividad: logins, logins fallidos, creaciones, cambios |

### Otros
| Método | Ruta | Acceso |
|---|---|:---:|
| GET | `/` y `/api/salud` | 🔓 |

**Ejemplo de uso con token:**
```bash
# login
curl -X POST http://127.0.0.1:5000/api/auth/login -H "Content-Type: application/json" \
     -d "{\"email\": \"admin@gastrobar.com\", \"password\": \"********\"}"

# usar el token
curl http://127.0.0.1:5000/api/productos -H "Authorization: Bearer <access_token>"
```

---

## 6. Casos de uso y cómo se cumplen

| # | Caso de uso | Actor | Endpoint |
|---|---|---|---|
| CU01 | Registrarse en el sistema | Empleado | `POST /api/auth/registro` |
| CU02 | Iniciar sesión | Admin, Empleado | `POST /api/auth/login` |
| CU03 | Gestionar categorías | Admin | `/api/categorias` |
| CU04 | Gestionar proveedores | Admin | `/api/proveedores` |
| CU05 | Gestionar productos | Admin | `/api/productos` |
| CU06 | Consultar productos y su detalle | Admin, Empleado | `GET /api/productos`, `/api/productos/<id>/detalle` |
| CU07 | Gestionar fichas con atributos variables | Admin | `/api/fichas` |
| CU08 | Registrar una venta (salida) | Admin, Empleado | `POST /api/movimientos` tipo `salida` |
| CU09 | Registrar una pérdida (merma) | Admin, Empleado | `POST /api/movimientos` tipo `merma` |
| CU10 | Registrar llegada de pedido (entrada) | Admin | `POST /api/movimientos` tipo `entrada` |
| CU11 | Anular un movimiento | Admin | `DELETE /api/movimientos/<id>` |
| CU12 | Ver productos con stock bajo | Admin | `GET /api/reportes/stock-bajo` |
| CU13 | Ver productos más vendidos | Admin | `GET /api/reportes/mas-vendidos` |
| CU14 | Consultar actividad del sistema | Admin | `GET /api/logs` |
| CU15 | Gestionar usuarios y roles | Admin | `/api/usuarios` |

---

## 7. Evidencias de ejecución

Todas las pruebas se hicieron en Postman, con un usuario **admin** (`admin@gastrobar.com`) y un **empleado** (`juan@gastrobar.com`). Las capturas están en `docs/evidencias/entrega3/`.

### 7.1 Tabla de usuarios en MySQL
La tabla `usuarios` se crea sola al arrancar la app. La contraseña se guarda en `password_hash`.

![Tabla usuarios](docs/evidencias/entrega3/17_tabla_usuarios_mysql.png)

### 7.2 Login (la API consulta MySQL y devuelve el JWT)
**Login del empleado** → 200, token con rol `empleado`
![Login empleado](docs/evidencias/entrega3/01_login_empleado.png)

**Login del admin** → 200, token con rol `admin`
![Login admin](docs/evidencias/entrega3/02_login_admin.png)

### 7.3 Ruta protegida con y sin token
**`GET /api/auth/yo` con token** → 200
![Con token](docs/evidencias/entrega3/03_yo_con_token.png)

**La misma ruta sin token** → 401 `Missing Authorization Header`
![Sin token](docs/evidencias/entrega3/04_yo_sin_token.png)

### 7.4 Roles (RBAC): admin vs empleado

| Prueba | Admin | Empleado |
|---|---|---|
| Crear producto | 201 | 403 |
| Reporte stock bajo | 200 | 403 |
| Listar usuarios | 200 | 403 |
| Registrar venta (salida) | — | 201 |
| Registrar entrada de pedido | 201 | 403 |

**Crear producto — admin** → 201
![](docs/evidencias/entrega3/05_crear_producto_admin_201.png)

**Crear producto — empleado** → 403 `Acceso denegado: se requiere rol admin`
![](docs/evidencias/entrega3/06_crear_producto_empleado_403.png)

**Reporte stock bajo — admin** → 200
![](docs/evidencias/entrega3/07_stock_bajo_admin_200.png)

**Reporte stock bajo — empleado** → 403
![](docs/evidencias/entrega3/08_stock_bajo_empleado_403.png)

**Listar usuarios — admin** → 200 (sin mostrar el `password_hash`)
![](docs/evidencias/entrega3/09_usuarios_admin_200.png)

**Listar usuarios — empleado** → 403
![](docs/evidencias/entrega3/10_usuarios_empleado_403.png)

**Venta registrada por el empleado** → 201. El campo `usuario` sale del token.
![](docs/evidencias/entrega3/11_venta_empleado_201.png)

**Entrada de pedido — empleado** → 403 `Un empleado solo puede registrar salidas y mermas`
![](docs/evidencias/entrega3/12_entrada_empleado_403.png)

**Entrada de pedido — admin** → 201 (stock 53 → 77)
![](docs/evidencias/entrega3/13_entrada_admin_201.png)

### 7.5 Usuario desactivado
**El admin desactiva al empleado** → 200, `activo: false`
![](docs/evidencias/entrega3/14_desactivar_usuario.png)

**El empleado intenta usar su token (todavía no vencido)** → 401 `Usuario inactivo o inexistente`
![](docs/evidencias/entrega3/15_token_usuario_inactivo_401.png)

**El admin lo reactiva** → 200, `activo: true`
![](docs/evidencias/entrega3/16_reactivar_usuario.png)

### 7.6 Prueba automática
`python scripts/probar_api.py` crea datos, inicia sesión como admin y llama los endpoints principales. La salida queda en [`docs/evidencias/salida_pruebas.md`](docs/evidencias/salida_pruebas.md).

---

## 8. Persistencia políglota (Entrega 2, resumen)

La unión entre MySQL y MongoDB es `producto_id`. Al registrar un movimiento:
1. Se valida el producto y el stock en MySQL.
2. Se cambia el stock en MySQL **sin commit**.
3. Se guarda el movimiento en MongoDB.
4. Si Mongo responde bien → `commit`; si falla → `rollback`, y el stock no cambia.

La justificación completa de la estructura NoSQL está en `docs/Entrega2_NoSQL_Justificacion.pdf`.
