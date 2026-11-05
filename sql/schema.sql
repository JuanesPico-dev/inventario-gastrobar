-- =========================================================
--  Inventario Gastrobar - Estructura SQL (MySQL)
--  (Flask-SQLAlchemy crea estas tablas solo con db.create_all(),
--   este script queda como documentación / para crearlas a mano)
-- =========================================================
CREATE DATABASE IF NOT EXISTS inventario_gastrobar
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE inventario_gastrobar;

CREATE TABLE IF NOT EXISTS categorias (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  nombre      VARCHAR(60)  NOT NULL UNIQUE,
  descripcion VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS proveedores (
  id       INT AUTO_INCREMENT PRIMARY KEY,
  nombre   VARCHAR(100) NOT NULL,
  nit      VARCHAR(20) UNIQUE,
  telefono VARCHAR(20),
  email    VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS productos (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  codigo_barras  VARCHAR(30) UNIQUE,
  nombre         VARCHAR(100)  NOT NULL,
  unidad         VARCHAR(20)   NOT NULL DEFAULT 'unidad',
  precio_compra  DECIMAL(10,2) NOT NULL DEFAULT 0,
  precio_venta   DECIMAL(10,2) NOT NULL DEFAULT 0,
  stock_actual   INT           NOT NULL DEFAULT 0,
  stock_minimo   INT           NOT NULL DEFAULT 5,
  activo         BOOLEAN       NOT NULL DEFAULT TRUE,
  creado_en      DATETIME      DEFAULT CURRENT_TIMESTAMP,
  categoria_id   INT NOT NULL,
  proveedor_id   INT,
  CONSTRAINT fk_prod_categoria FOREIGN KEY (categoria_id) REFERENCES categorias(id),
  CONSTRAINT fk_prod_proveedor FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
);
