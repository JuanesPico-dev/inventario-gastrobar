# Evidencias de ejecución (salida automática)

## 1. Conexión a las dos bases

`GET /api/salud` → **200**

Respuesta:
```json
{
  "mysql": "conectado",
  "mongodb": "conectado"
}
```

## 2. CREATE categoría (MySQL)

`POST /api/categorias` → **201**

Body enviado:
```json
{
  "nombre": "Cócteles",
  "descripcion": "Preparados en barra"
}
```

Respuesta:
```json
{
  "id": 6,
  "nombre": "Cócteles",
  "descripcion": "Preparados en barra"
}
```

## 3. CREATE producto (MySQL)

`POST /api/productos` → **201**

Body enviado:
```json
{
  "codigo_barras": "7700000999",
  "nombre": "Ron Viejo de Caldas 750ml",
  "unidad": "botella",
  "precio_compra": 42000,
  "precio_venta": 95000,
  "stock_actual": 4,
  "stock_minimo": 3,
  "categoria_id": 2,
  "proveedor_id": 2
}
```

Respuesta:
```json
{
  "id": 10,
  "codigo_barras": "7700000999",
  "nombre": "Ron Viejo de Caldas 750ml",
  "unidad": "botella",
  "precio_compra": 42000.0,
  "precio_venta": 95000.0,
  "stock_actual": 4,
  "stock_minimo": 3,
  "activo": true,
  "categoria": "Licores",
  "proveedor": "Distribuidora La 80"
}
```

## 4. READ productos de la categoría Licores (MySQL)

`GET /api/productos?categoria_id=2` → **200**

Respuesta:
```json
[
  {
    "id": 3,
    "codigo_barras": "7702049001",
    "nombre": "Aguardiente Antioqueño Tapa Azul 750ml",
    "unidad": "botella",
    "precio_compra": 38000.0,
    "precio_venta": 85000.0,
    "stock_actual": 19,
    "stock_minimo": 5,
    "activo": true,
    "categoria": "Licores",
    "proveedor": "Distribuidora La 80"
  },
  {
    "id": 10,
    "codigo_barras": "7700000999",
    "nombre": "Ron Viejo de Caldas 750ml",
    "unidad": "botella",
    "precio_compra": 42000.0,
    "precio_venta": 95000.0,
    "stock_actual": 4,
    "stock_minimo": 3,
    "activo": true,
    "categoria": "Licores",
    "proveedor": "Distribuidora La 80"
  },
  {
    "id": 4,
    "codigo_barras": "5000267014",
    "nombre": "Whisky Johnnie Walker Red 700ml",
    "unidad": "botella",
    "precio_compra": 65000.0,
    "precio_venta": 160000.0,
    "stock_actual": 10,
    "stock_minimo": 2,
    "activo": true,
    "categoria": "Licores",
    "proveedor": "Distribuidora La 80"
  }
]
```

## 5. UPDATE precio (MySQL)

`PUT /api/productos/10` → **200**

Body enviado:
```json
{
  "precio_venta": 98000
}
```

Respuesta:
```json
{
  "id": 10,
  "codigo_barras": "7700000999",
  "nombre": "Ron Viejo de Caldas 750ml",
  "unidad": "botella",
  "precio_compra": 42000.0,
  "precio_venta": 98000.0,
  "stock_actual": 4,
  "stock_minimo": 3,
  "activo": true,
  "categoria": "Licores",
  "proveedor": "Distribuidora La 80"
}
```

## 6. CREATE ficha con atributos variables (MongoDB)

`POST /api/fichas` → **201**

Body enviado:
```json
{
  "producto_id": 10,
  "tipo": "licor",
  "atributos": {
    "grados_alcohol": 35,
    "volumen_ml": 750,
    "anos_anejamiento": 3
  },
  "etiquetas": [
    "nacional"
  ]
}
```

Respuesta:
```json
{
  "producto_id": 10,
  "tipo": "licor",
  "atributos": {
    "grados_alcohol": 35,
    "volumen_ml": 750,
    "anos_anejamiento": 3
  },
  "etiquetas": [
    "nacional"
  ],
  "notas": null,
  "actualizado": "2026-11-04T02:11:58.853913",
  "_id": "6aea946edff010f5ec884985"
}
```

## 7. UPDATE ficha: se agrega un atributo nuevo sin cambiar ninguna tabla (MongoDB)

`PUT /api/fichas/10` → **200**

Body enviado:
```json
{
  "atributos": {
    "sabor": "tradicional"
  }
}
```

Respuesta:
```json
{
  "producto_id": 10,
  "tipo": "licor",
  "atributos": {
    "grados_alcohol": 35,
    "volumen_ml": 750,
    "anos_anejamiento": 3,
    "sabor": "tradicional"
  },
  "etiquetas": [
    "nacional"
  ],
  "notas": null,
  "actualizado": "2026-11-04T02:11:58.854000",
  "_id": "6aea946edff010f5ec884985"
}
```

## 8. READ fichas filtradas por tipo (MongoDB)

`GET /api/fichas?tipo=cerveza` → **200**

Respuesta:
```json
[
  {
    "producto_id": 1,
    "notas": null,
    "etiquetas": [
      "nacional",
      "mas_pedida"
    ],
    "actualizado": "2026-11-04T02:11:58.801000",
    "tipo": "cerveza",
    "atributos": {
      "grados_alcohol": 4.7,
      "volumen_ml": 330,
      "estilo": "lager",
      "retornable": true
    },
    "_id": "6aea946edff010f5ec88486e"
  },
  {
    "producto_id": 2,
    "notas": null,
    "etiquetas": [
      "importada"
    ],
    "actualizado": "2026-11-04T02:11:58.803000",
    "tipo": "cerveza",
    "atributos": {
      "grados_alcohol": 4.5,
      "volumen_ml": 355,
      "estilo": "pilsner",
      "retornable": false,
      "pais_origen": "México"
    },
    "_id": "6aea946edff010f5ec88486f"
  }
]
```

## 9. CREATE movimiento de ENTRADA: guarda en Mongo y sube stock en MySQL

`POST /api/movimientos` → **201**

Body enviado:
```json
{
  "producto_id": 10,
  "tipo": "entrada",
  "cantidad": 12,
  "usuario": "jhon",
  "motivo": "Pedido semanal",
  "detalle": {
    "factura_proveedor": "FV-2231",
    "lote": "L5521"
  }
}
```

Respuesta:
```json
{
  "producto_id": 10,
  "producto_nombre": "Ron Viejo de Caldas 750ml",
  "tipo": "entrada",
  "cantidad": 12,
  "stock_anterior": 4,
  "stock_resultante": 16,
  "usuario": "jhon",
  "motivo": "Pedido semanal",
  "detalle": {
    "factura_proveedor": "FV-2231",
    "lote": "L5521"
  },
  "fecha": "2026-11-04T02:11:58.856718",
  "_id": "6aea946edff010f5ec884988",
  "alerta_stock_bajo": false
}
```

## 10. CREATE movimiento de SALIDA con detalle distinto (mesa/comanda)

`POST /api/movimientos` → **201**

Body enviado:
```json
{
  "producto_id": 10,
  "tipo": "salida",
  "cantidad": 3,
  "usuario": "mesero1",
  "detalle": {
    "mesa": 4,
    "comanda": 5120
  }
}
```

Respuesta:
```json
{
  "producto_id": 10,
  "producto_nombre": "Ron Viejo de Caldas 750ml",
  "tipo": "salida",
  "cantidad": 3,
  "stock_anterior": 16,
  "stock_resultante": 13,
  "usuario": "mesero1",
  "motivo": null,
  "detalle": {
    "mesa": 4,
    "comanda": 5120
  },
  "fecha": "2026-11-04T02:11:58.860773",
  "_id": "6aea946edff010f5ec88498a",
  "alerta_stock_bajo": false
}
```

## 11. Validación: salida mayor al stock (debe fallar)

`POST /api/movimientos` → **409**

Body enviado:
```json
{
  "producto_id": 10,
  "tipo": "salida",
  "cantidad": 500
}
```

Respuesta:
```json
{
  "error": "Stock insuficiente. Hay 13 botella(s)"
}
```

## 12. UPDATE movimiento (MongoDB)

`PUT /api/movimientos/6aea946edff010f5ec88498a` → **200**

Body enviado:
```json
{
  "motivo": "Venta mesa 4 - cumpleaños"
}
```

Respuesta:
```json
{
  "producto_id": 10,
  "producto_nombre": "Ron Viejo de Caldas 750ml",
  "tipo": "salida",
  "cantidad": 3,
  "stock_anterior": 16,
  "stock_resultante": 13,
  "usuario": "mesero1",
  "motivo": "Venta mesa 4 - cumpleaños",
  "detalle": {
    "mesa": 4,
    "comanda": 5120
  },
  "fecha": "2026-11-04T02:11:58.860000",
  "_id": "6aea946edff010f5ec88498a",
  "editado_en": "2026-11-04T02:11:58.864000"
}
```

## 13. DELETE (anular) movimiento: se borra de Mongo y se revierte stock en MySQL

`DELETE /api/movimientos/6aea946edff010f5ec884988` → **200**

Respuesta:
```json
{
  "mensaje": "Movimiento anulado y stock revertido",
  "stock_actual": 1
}
```

## 14. Stock en MySQL después de anular

`GET /api/productos/10` → **200**

Respuesta:
```json
{
  "id": 10,
  "codigo_barras": "7700000999",
  "nombre": "Ron Viejo de Caldas 750ml",
  "unidad": "botella",
  "precio_compra": 42000.0,
  "precio_venta": 98000.0,
  "stock_actual": 1,
  "stock_minimo": 3,
  "activo": true,
  "categoria": "Licores",
  "proveedor": "Distribuidora La 80"
}
```

## 15. ⭐ ENDPOINT COMBINADO: producto (MySQL) + ficha y últimos 10 movimientos (MongoDB)

`GET /api/productos/1/detalle` → **200**

Respuesta:
```json
{
  "producto": {
    "id": 1,
    "codigo_barras": "7702004001",
    "nombre": "Cerveza Club Colombia Dorada 330ml",
    "unidad": "botella",
    "precio_compra": 2500.0,
    "precio_venta": 6000.0,
    "stock_actual": 55,
    "stock_minimo": 48,
    "activo": true,
    "categoria": "Cervezas",
    "proveedor": {
      "id": 1,
      "nombre": "Bavaria S.A.",
      "nit": "860005224-6",
      "telefono": "6013099000",
      "email": "pedidos@bavaria.com.co"
    },
    "alerta_stock_bajo": false
  },
  "ficha": {
    "notas": null,
    "etiquetas": [
      "nacional",
      "mas_pedida"
    ],
    "actualizado": "2026-11-04T02:11:58.801000",
    "tipo": "cerveza",
    "atributos": {
      "grados_alcohol": 4.7,
      "volumen_ml": 330,
      "estilo": "lager",
      "retornable": true
    }
  },
  "ultimos_movimientos": [
    {
      "producto_id": 1,
      "producto_nombre": "Cerveza Club Colombia Dorada 330ml",
      "tipo": "salida",
      "cantidad": 13,
      "stock_anterior": 68,
      "stock_resultante": 55,
      "usuario": "mesero1",
      "motivo": null,
      "detalle": {
        "mesa": 8,
        "comanda": 8634
      },
      "fecha": "2026-11-03T22:11:58.807000",
      "_id": "6aea946edff010f5ec88489a"
    },
    {
      "producto_id": 1,
      "producto_nombre": "Cerveza Club Colombia Dorada 330ml",
      "tipo": "salida",
      "cantidad": 30,
      "stock_anterior": 98,
      "stock_resultante": 68,
      "usuario": "mesero1",
      "motivo": null,
      "detalle": {
        "mesa": 5,
        "comanda": 6691
      },
      "fecha": "2026-11-02T23:11:58.807000",
      "_id": "6aea946edff010f5ec884899"
    },
    {
      "producto_id": 1,
      "producto_nombre": "Cerveza Club Colombia Dorada 330ml",
      "tipo": "salida",
      "cantidad": 29,
      "stock_anterior": 127,
      "stock_resultante": 98,
      "usuario": "mesero2",
      "motivo": null,
      "detalle": {
        "mesa": 1,
        "comanda": 2152
      },
      "fecha": "2026-11-01T20:11:58.807000",
      "_id": "6aea946edff010f5ec884898"
    },
    {
      "producto_id": 1,
      "producto_nombre": "Cerveza Club Colombia Dorada 330ml",
      "tipo": "salida",
      "cantidad": 10,
      "stock_anterior": 137,
      "stock_resultante": 127,
      "usuario": "jhon",
      "motivo": null,
      "detalle": {
        "mesa": 10,
        "comanda": 3478
      },
      "fecha": "2026-10-31T23:11:58.807000",
      "_id": "6aea946edff010f5ec884897"
    },
    {
      "producto_id": 1,
      "producto_nombre": "Cerveza Club Colombia Dorada 330ml",
      "tipo": "salida",
      "cantidad": 24,
      "stock_anterior": 161,
      "stock_resultante": 137,
      "usuario": "mesero2",
      "motivo": null,
      "detalle": {
        "mesa": 3,
        "comanda": 2801
      },
      "fecha": "2026-10-30T21:11:58.807000",
      "_id": "6aea946edff010f5ec884896"
    },
    {
      "producto_id": 1,
      "producto_nombre": "Cerveza Club Colombia Dorada 330ml",
      "tipo": "salida",
      "cantidad": 30,
      "stock_anterior": 191,
      "stock_resultante": 161,
      "usuario": "jhon",
      "motivo": null,
      "detalle": {
        "mesa": 7,
        "comanda": 2019
      },
      "fecha": "2026-10-29T20:11:58.807000",
      "_id": "6aea946edff010f5ec884895"
    },
    {
      "producto_id": 1,
      "producto_nombre": "Cerveza Club Colombia Dorada 330ml",
      "tipo": "salida",
      "cantidad": 27,
      "stock_anterior": 218,
      "stock_resultante": 191,
      "usuario": "mesero1",
      "motivo": null,
      "detalle": {
        "mesa": 7,
        "comanda": 7521
      },
      "fecha": "2026-10-28T22:11:58.807000",
      "_id": "6aea946edff010f5ec884894"
    },
    {
      "producto_id": 1,
      "producto_nombre": "Cerveza Club Colombia Dorada 330ml",
      "tipo": "entrada",
      "cantidad": 150,
      "stock_anterior": 68,
      "stock_resultante": 218,
      "usuario": "mesero1",
      "motivo": "Pedido semanal",
      "detalle": {
        "factura_proveedor": "FV-732",
        "lote": "L1884"
      },
      "fecha": "2026-10-28T14:11:58.807000",
      "_id": "6aea946edff010f5ec884893"
    },
    {
      "producto_id": 1,
      "producto_nombre": "Cerveza Club Colombia Dorada 330ml",
      "tipo": "salida",
      "cantidad": 21,
      "stock_anterior": 89,
      "stock_resultante": 68,
      "usuario": "mesero2",
      "motivo": null,
      "detalle": {
        "mesa": 10,
        "comanda": 6220
      },
      "fecha": "2026-10-27T20:11:58.807000",
      "_id": "6aea946edff010f5ec884892"
    },
    {
      "producto_id": 1,
      "producto_nombre": "Cerveza Club Colombia Dorada 330ml",
      "tipo": "salida",
      "cantidad": 15,
      "stock_anterior": 104,
      "stock_resultante": 89,
      "usuario": "jhon",
      "motivo": null,
      "detalle": {
        "mesa": 5,
        "comanda": 5619
      },
      "fecha": "2026-10-26T19:11:58.807000",
      "_id": "6aea946edff010f5ec884891"
    }
  ],
  "fuentes": {
    "producto": "MySQL",
    "ficha": "MongoDB",
    "ultimos_movimientos": "MongoDB"
  }
}
```

## 16. ⭐ REPORTE COMBINADO: stock bajo (MySQL) + consumo de 7 días (MongoDB)

`GET /api/reportes/stock-bajo?dias=7` → **200**

Respuesta:
```json
{
  "periodo_dias": 7,
  "total": 3,
  "productos": [
    {
      "producto_id": 6,
      "nombre": "Agua Cristal 600ml",
      "proveedor": "Postobón",
      "stock_actual": 0,
      "stock_minimo": 20,
      "consumo_ultimos_7_dias": 24,
      "consumo_promedio_dia": 3.43,
      "dias_estimados_restantes": 0.0
    },
    {
      "producto_id": 9,
      "nombre": "Vasos plásticos 7oz x50",
      "proveedor": "Surtidor Plaza Paloquemao",
      "stock_actual": 1,
      "stock_minimo": 4,
      "consumo_ultimos_7_dias": 8,
      "consumo_promedio_dia": 1.14,
      "dias_estimados_restantes": 0.9
    },
    {
      "producto_id": 10,
      "nombre": "Ron Viejo de Caldas 750ml",
      "proveedor": "Distribuidora La 80",
      "stock_actual": 1,
      "stock_minimo": 3,
      "consumo_ultimos_7_dias": 3,
      "consumo_promedio_dia": 0.43,
      "dias_estimados_restantes": 2.3
    }
  ]
}
```

## 17. ⭐ REPORTE COMBINADO: más vendidos (MongoDB) + precios (MySQL)

`GET /api/reportes/mas-vendidos?dias=30&top=5` → **200**

Respuesta:
```json
{
  "periodo_dias": 30,
  "top": [
    {
      "producto_id": 1,
      "nombre": "Cerveza Club Colombia Dorada 330ml",
      "categoria": "Cervezas",
      "unidades_vendidas": 588,
      "numero_salidas": 30,
      "ingreso_estimado": 3528000.0
    },
    {
      "producto_id": 5,
      "nombre": "Coca-Cola 400ml",
      "categoria": "Bebidas sin alcohol",
      "unidades_vendidas": 215,
      "numero_salidas": 30,
      "ingreso_estimado": 967500.0
    },
    {
      "producto_id": 2,
      "nombre": "Cerveza Corona 355ml",
      "categoria": "Cervezas",
      "unidades_vendidas": 137,
      "numero_salidas": 30,
      "ingreso_estimado": 1233000.0
    },
    {
      "producto_id": 6,
      "nombre": "Agua Cristal 600ml",
      "categoria": "Bebidas sin alcohol",
      "unidades_vendidas": 111,
      "numero_salidas": 29,
      "ingreso_estimado": 333000.0
    },
    {
      "producto_id": 7,
      "nombre": "Papa criolla (kg)",
      "categoria": "Comidas",
      "unidades_vendidas": 44,
      "numero_salidas": 30,
      "ingreso_estimado": 0.0
    }
  ]
}
```

## 18. Logs de actividad (MongoDB)

`GET /api/logs?limite=5` → **200**

Respuesta:
```json
[
  {
    "accion": "ELIMINAR",
    "entidad": "movimiento",
    "entidad_id": "6aea946edff010f5ec884988",
    "usuario": "sistema",
    "datos": {
      "producto_id": 10
    },
    "fecha": "2026-11-04T02:11:58.869000",
    "_id": "6aea946edff010f5ec88498d"
  },
  {
    "accion": "ACTUALIZAR",
    "entidad": "movimiento",
    "entidad_id": "6aea946edff010f5ec88498a",
    "usuario": "sistema",
    "datos": {
      "motivo": "Venta mesa 4 - cumpleaños"
    },
    "fecha": "2026-11-04T02:11:58.865000",
    "_id": "6aea946edff010f5ec88498c"
  },
  {
    "accion": "CREAR",
    "entidad": "movimiento",
    "entidad_id": "6aea946edff010f5ec88498a",
    "usuario": "mesero1",
    "datos": {
      "producto_id": 10,
      "tipo": "salida",
      "cantidad": 3
    },
    "fecha": "2026-11-04T02:11:58.862000",
    "_id": "6aea946edff010f5ec88498b"
  },
  {
    "accion": "CREAR",
    "entidad": "movimiento",
    "entidad_id": "6aea946edff010f5ec884988",
    "usuario": "jhon",
    "datos": {
      "producto_id": 10,
      "tipo": "entrada",
      "cantidad": 12
    },
    "fecha": "2026-11-04T02:11:58.859000",
    "_id": "6aea946edff010f5ec884989"
  },
  {
    "accion": "ACTUALIZAR",
    "entidad": "ficha",
    "entidad_id": 10,
    "usuario": "sistema",
    "datos": {
      "atributos": {
        "sabor": "tradicional"
      }
    },
    "fecha": "2026-11-04T02:11:58.855000",
    "_id": "6aea946edff010f5ec884987"
  }
]
```

## 19. DELETE producto (MySQL) y su ficha (MongoDB)

`DELETE /api/productos/10` → **200**

Respuesta:
```json
{
  "mensaje": "Producto eliminado"
}
```

## 20. DELETE categoría (MySQL)

`DELETE /api/categorias/6` → **200**

Respuesta:
```json
{
  "mensaje": "Categoría eliminada"
}
```
