"""
database.py — Módulo de inicialización de la base de datos
Proyecto: Acumatica ERP Prototipo · SIS-315 USFX 2025

Este módulo crea todas las tablas y carga datos de ejemplo bolivianos.
La función init_db() es idempotente: puede ejecutarse varias veces sin
duplicar datos, ya que verifica si la BD ya fue inicializada.
"""

import sqlite3


# ─────────────────────────────────────────────────────────────────────────────
# DEFINICIÓN DE TABLAS SQL
# ─────────────────────────────────────────────────────────────────────────────

SQL_CREAR_TABLAS = """
-- Tabla de clientes / CRM
CREATE TABLE IF NOT EXISTS clientes (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre           TEXT    NOT NULL,
    empresa          TEXT,
    email            TEXT,
    telefono         TEXT,
    ciudad           TEXT,
    direccion        TEXT,
    estado           TEXT    DEFAULT 'Activo',
    fecha_registro   TEXT    DEFAULT (date('now'))
);

-- Tabla de productos / inventario
CREATE TABLE IF NOT EXISTS productos (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre           TEXT    NOT NULL,
    descripcion      TEXT,
    categoria        TEXT,
    precio_unitario  REAL,
    stock            INTEGER DEFAULT 0,
    stock_minimo     INTEGER DEFAULT 10,
    unidad           TEXT    DEFAULT 'und',
    estado           TEXT    DEFAULT 'Activo',
    fecha_creacion   TEXT    DEFAULT (date('now'))
);

-- Tabla de facturas (cabecera)
CREATE TABLE IF NOT EXISTS facturas (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    numero             TEXT    UNIQUE,
    cliente_id         INTEGER,
    fecha_emision      TEXT,
    fecha_vencimiento  TEXT,
    subtotal           REAL,
    descuento          REAL    DEFAULT 0,
    total              REAL,
    estado             TEXT    DEFAULT 'Pendiente',
    notas              TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

-- Tabla de ítems de factura (detalle / líneas)
CREATE TABLE IF NOT EXISTS factura_items (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    factura_id       INTEGER,
    producto_id      INTEGER,
    descripcion      TEXT,
    cantidad         INTEGER,
    precio_unitario  REAL,
    subtotal         REAL,
    FOREIGN KEY (factura_id)  REFERENCES facturas(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- Tabla de gastos operativos
CREATE TABLE IF NOT EXISTS gastos (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    concepto     TEXT    NOT NULL,
    categoria    TEXT,
    monto        REAL,
    fecha        TEXT,
    descripcion  TEXT
);
"""


# ─────────────────────────────────────────────────────────────────────────────
# DATOS SEED — CLIENTES (mínimo 10, empresas reales de Bolivia)
# ─────────────────────────────────────────────────────────────────────────────

SEED_CLIENTES = [
    # (nombre, empresa, email, telefono, ciudad, direccion, estado)
    ('Carlos Quispe Mamani',   'Tigo Bolivia S.A.',               'carlos.quispe@tigo.com.bo',      '72345678', 'La Paz',       'Av. Arce Nro. 2631, Sopocachi',          'Activo'),
    ('María Flores Condori',   'YPFB Corporación',                'mflores@ypfb.com.bo',            '71234567', 'La Paz',       'Av. 6 de Agosto Nro. 2742',              'Activo'),
    ('Jorge Salinas Vaca',     'Banco BNB S.A.',                  'jsalinas@bnb.com.bo',            '78901234', 'Cochabamba',   'Av. Heroínas Nro. 156, Centro',          'Activo'),
    ('Lucía Torrez Espinoza',  'Sofía Ltda.',                     'ltorrez@sofia.com.bo',           '69876543', 'Santa Cruz',   'Parque Industrial PI-7, Manzana 12',     'Activo'),
    ('Roberto Chumacero Vega', 'Entel Bolivia',                   'rchumacero@entel.com.bo',        '76543210', 'La Paz',       'Plaza del Estudiante, Edif. Entel',      'Activo'),
    ('Sandra Medina Álvarez',  'Farmacorp S.A.',                  'smedina@farmacorp.com.bo',       '63210987', 'Santa Cruz',   'Av. Cañoto Nro. 1200',                   'Activo'),
    ('Fernando Rojas Gutierrez','Supermercados Ketal S.R.L.',     'frojas@ketal.com.bo',            '77654321', 'La Paz',       'Av. Ballivián Nro. 1560, Calacoto',      'Activo'),
    ('Patricia Ávila Montaño', 'CRE — Cooperativa Rural de Electrificación', 'pavila@cre.com.bo', '68543210', 'Santa Cruz',   'Av. Alemana Nro. 50, Zona Norte',        'Activo'),
    ('Diego Zenteno Pardo',    'Fancesa S.A.',                    'dzenteno@fancesa.com.bo',        '72109876', 'Sucre',        'Parque Industrial, Av. Circunvalación',  'Activo'),
    ('Carla Ibáñez Vargas',    'Cervecería Boliviana Nacional S.A.', 'cibañez@cbn.com.bo',         '71098765', 'Cochabamba',   'Av. Blanco Galindo Km 7',                'Activo'),
    ('Hugo Mamani Ticona',     'Embol S.A. (Coca-Cola Bolivia)',  'hmamani@embol.com.bo',           '79870123', 'Santa Cruz',   'Av. Roca y Coronado Nro. 900',           'Activo'),
    ('Verónica Lara Choque',   'Boliviana de Aviación (BoA)',     'vlara@boa.bo',                   '67123456', 'Cochabamba',   'Aeropuerto Internacional J. Wilstermann','Inactivo'),
    ('Andrés Villca Quispe',   'Cementos Warnes S.A.',            'avillca@warnes.com.bo',          '75432198', 'Warnes',       'Carretera a Warnes Km 14',               'Activo'),
    ('Gloria Soto Pérez',      'Industrias de Aceite S.A. (FINO)','gsoto@fino.com.bo',             '64321987', 'Santa Cruz',   'Av. Grigotá Km 5, Zona Parque Industrial','Inactivo'),
]


# ─────────────────────────────────────────────────────────────────────────────
# DATOS SEED — PRODUCTOS (mínimo 15, con categorías variadas)
# ─────────────────────────────────────────────────────────────────────────────

SEED_PRODUCTOS = [
    # (nombre, descripcion, categoria, precio_unitario, stock, stock_minimo, unidad)
    # Tecnología
    ('Laptop Dell Inspiron 15',   'Intel i5 12ª gen, 16GB RAM, 512GB SSD',        'Tecnología',    6800.00, 25, 5,  'und'),
    ('Monitor LG 24" Full HD',    'Resolución 1920x1080, Panel IPS, HDMI',         'Tecnología',    1950.00, 18, 5,  'und'),
    ('Teclado Mecánico Redragon', 'Switch Red, retroiluminación RGB, USB',         'Tecnología',     450.00,  8, 10, 'und'),  # stock bajo
    ('Mouse Inalámbrico Logitech','DPI 2400, autonomía 12 meses, USB nano',        'Tecnología',     280.00, 32, 10, 'und'),
    ('Disco Duro Externo 1TB',    'USB 3.0, WD Elements, lectura 120MB/s',         'Tecnología',     650.00,  5, 10, 'und'),  # stock bajo
    # Oficina
    ('Resma Papel Bond A4 75g',   'Paquete 500 hojas, blancura 96%, libre de ácido','Oficina',        45.00, 120, 20, 'paq'),
    ('Bolígrafos BIC Cristal x12','Caja 12 unidades, punta media, tinta azul',    'Oficina',         28.00,  85, 20, 'cja'),
    ('Archivador AZ Oficio',      'Ancho 8cm, forro vinílico, palanca metálica',   'Oficina',         32.00,  60, 15, 'und'),
    ('Tóner HP LaserJet 85A',     'Rendimiento aprox. 1600 páginas, Negro',        'Oficina',        320.00,  7, 10, 'und'),  # stock bajo
    # Manufactura / Industria
    ('Cemento Fancesa 50kg',      'Cemento Portland IP-30, resistencia normal',    'Manufactura',     65.00, 200, 50, 'bol'),
    ('Pintura Látex Interior 4L', 'Base agua, semi-lavable, color blanco humo',    'Manufactura',    120.00,  45, 20, 'gal'),
    ('Tubo PVC 4" x 3m',          'Para instalaciones sanitarias, presión 8 bar', 'Manufactura',     55.00,  90, 30, 'und'),
    # Alimentos
    ('Aceite FINO 1L',            'Aceite de girasol refinado, sin colesterol',    'Alimentos',       16.50, 180, 40, 'bot'),
    ('Azúcar Blanca 1kg',         'Azúcar refinada de caña, cristal fino',         'Alimentos',       12.00, 250, 50, 'bol'),
    ('Harina de Trigo 50kg',      'Tipo 000, para panadería y repostería',         'Alimentos',      220.00,  3, 15, 'bol'),  # stock bajo (sin stock casi)
    # Servicios
    ('Licencia Office 365 (anual)','Microsoft 365 Business Basic, 1 usuario',     'Servicios',       850.00, 40, 5,  'lic'),
    ('Servicio de Mantenimiento PC','Limpieza, actualización de drivers y antivirus','Servicios',    150.00, 999, 1,  'svc'),  # servicio ilimitado
]


# ─────────────────────────────────────────────────────────────────────────────
# DATOS SEED — FACTURAS con sus ítems (mínimo 15)
# ─────────────────────────────────────────────────────────────────────────────

# Formato: (numero, cliente_id, fecha_emision, fecha_vencimiento, descuento%, estado, notas, items)
# items: lista de (producto_id, descripcion, cantidad, precio_unitario)
SEED_FACTURAS = [
    (
        'FAC-2025-001', 1, '2025-01-10', '2025-02-10', 0, 'Pagada',
        'Equipamiento inicial para sucursal Sopocachi.',
        [(1, 'Laptop Dell Inspiron 15', 3, 6800.00),
         (2, 'Monitor LG 24" Full HD', 3, 1950.00)]
    ),
    (
        'FAC-2025-002', 2, '2025-01-15', '2025-02-15', 5, 'Pagada',
        'Suministros de oficina para las oficinas centrales YPFB.',
        [(6, 'Resma Papel Bond A4 75g', 50, 45.00),
         (7, 'Bolígrafos BIC Cristal x12', 20, 28.00),
         (8, 'Archivador AZ Oficio', 30, 32.00)]
    ),
    (
        'FAC-2025-003', 3, '2025-01-20', '2025-02-20', 0, 'Pagada',
        'Renovación de licencias de software.',
        [(16, 'Licencia Office 365 (anual)', 10, 850.00)]
    ),
    (
        'FAC-2025-004', 4, '2025-02-01', '2025-03-01', 10, 'Pagada',
        'Materiales para amplición de planta Sofía.',
        [(10, 'Cemento Fancesa 50kg', 100, 65.00),
         (12, 'Tubo PVC 4" x 3m', 50, 55.00)]
    ),
    (
        'FAC-2025-005', 5, '2025-02-10', '2025-03-10', 0, 'Pendiente',
        'Reposición mensual de insumos de oficina Entel.',
        [(6, 'Resma Papel Bond A4 75g', 30, 45.00),
         (9, 'Tóner HP LaserJet 85A', 5, 320.00)]
    ),
    (
        'FAC-2025-006', 6, '2025-02-14', '2025-03-14', 0, 'Pendiente',
        'Equipos de cómputo para nueva farmacia.',
        [(1, 'Laptop Dell Inspiron 15', 2, 6800.00),
         (3, 'Teclado Mecánico Redragon', 2, 450.00),
         (4, 'Mouse Inalámbrico Logitech', 2, 280.00)]
    ),
    (
        'FAC-2025-007', 7, '2025-02-20', '2025-03-05', 0, 'Vencida',
        'Suministros de limpieza y oficina Ketal.',
        [(11, 'Pintura Látex Interior 4L', 20, 120.00),
         (6,  'Resma Papel Bond A4 75g', 15, 45.00)]
    ),
    (
        'FAC-2025-008', 8, '2025-03-01', '2025-04-01', 0, 'Pagada',
        'Materiales eléctricos y construcción CRE.',
        [(10, 'Cemento Fancesa 50kg', 50, 65.00),
         (12, 'Tubo PVC 4" x 3m', 80, 55.00)]
    ),
    (
        'FAC-2025-009', 9, '2025-03-05', '2025-04-05', 15, 'Pagada',
        'Equipamiento tecnológico Fancesa planta Sucre.',
        [(1, 'Laptop Dell Inspiron 15', 5, 6800.00),
         (2, 'Monitor LG 24" Full HD', 5, 1950.00),
         (5, 'Disco Duro Externo 1TB', 5, 650.00)]
    ),
    (
        'FAC-2025-010', 10, '2025-03-10', '2025-04-10', 0, 'Pendiente',
        'Insumos alimenticios para evento corporativo CBN.',
        [(13, 'Aceite FINO 1L', 100, 16.50),
         (14, 'Azúcar Blanca 1kg', 200, 12.00)]
    ),
    (
        'FAC-2025-011', 11, '2025-03-15', '2025-03-30', 0, 'Vencida',
        'Materiales de construcción almacén Embol.',
        [(10, 'Cemento Fancesa 50kg', 80, 65.00),
         (11, 'Pintura Látex Interior 4L', 15, 120.00)]
    ),
    (
        'FAC-2025-012', 1, '2025-04-01', '2025-05-01', 5, 'Pagada',
        'Segunda compra de equipos Tigo regional.',
        [(4, 'Mouse Inalámbrico Logitech', 10, 280.00),
         (16, 'Licencia Office 365 (anual)', 5, 850.00)]
    ),
    (
        'FAC-2025-013', 3, '2025-04-10', '2025-05-10', 0, 'Pendiente',
        'Servicio de mantenimiento trimestral Banco BNB.',
        [(17, 'Servicio de Mantenimiento PC', 20, 150.00)]
    ),
    (
        'FAC-2025-014', 13, '2025-04-20', '2025-05-20', 0, 'Pagada',
        'Suministro de cemento Cementos Warnes.',
        [(10, 'Cemento Fancesa 50kg', 200, 65.00)]
    ),
    (
        'FAC-2025-015', 2, '2025-05-01', '2025-06-01', 10, 'Pendiente',
        'Equipamiento tecnológico YPFB offices 2025.',
        [(1, 'Laptop Dell Inspiron 15', 8, 6800.00),
         (2, 'Monitor LG 24" Full HD', 8, 1950.00),
         (9, 'Tóner HP LaserJet 85A', 10, 320.00)]
    ),
    (
        'FAC-2025-016', 5, '2025-05-10', '2025-06-10', 0, 'Pendiente',
        'Licencias y suministros Entel segundo trimestre.',
        [(16, 'Licencia Office 365 (anual)', 15, 850.00),
         (6,  'Resma Papel Bond A4 75g', 40, 45.00)]
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# DATOS SEED — GASTOS (mínimo 10)
# ─────────────────────────────────────────────────────────────────────────────

SEED_GASTOS = [
    # (concepto, categoria, monto, fecha, descripcion)
    ('Alquiler oficina central',          'Administración', 8500.00,  '2025-01-05', 'Pago mensual alquiler edificio zona central Sucre'),
    ('Servicios básicos (agua, luz, internet)', 'Administración', 1850.00, '2025-01-07', 'Factura SETAR, CESSA y NTT Bolivia enero'),
    ('Sueldos y salarios personal',       'Recursos Humanos', 45000.00, '2025-01-31', 'Planilla mensual 8 empleados enero 2025'),
    ('Mantenimiento vehicular',           'Operaciones',   1200.00,  '2025-02-03', 'Servicio y cambio de aceite 3 vehículos empresa'),
    ('Publicidad redes sociales',         'Marketing',      900.00,  '2025-02-15', 'Campaña Facebook Ads e Instagram febrero'),
    ('Sueldos y salarios personal',       'Recursos Humanos', 45000.00, '2025-02-28', 'Planilla mensual 8 empleados febrero 2025'),
    ('Alquiler oficina central',          'Administración', 8500.00,  '2025-02-05', 'Pago mensual alquiler edificio zona central Sucre'),
    ('Compra de insumos de limpieza',     'Operaciones',    380.00,  '2025-03-02', 'Desinfectantes, escobas, trapeadores oficina'),
    ('Viáticos viaje La Paz',             'Comercial',     2400.00,  '2025-03-12', 'Pasajes y estadía reunión con clientes La Paz'),
    ('Renovación dominio y hosting web',  'Tecnología',     750.00,  '2025-03-20', 'Dominio .com.bo anual + hosting VPS 1 año'),
    ('Sueldos y salarios personal',       'Recursos Humanos', 45000.00, '2025-03-31', 'Planilla mensual 8 empleados marzo 2025'),
    ('Alquiler oficina central',          'Administración', 8500.00,  '2025-04-05', 'Pago mensual alquiler edificio zona central Sucre'),
    ('Asesoría contable y legal',         'Administración', 1500.00,  '2025-04-10', 'Honorarios estudio contable trimestral Dra. Paz'),
    ('Material de escritorio',            'Administración',  620.00,  '2025-04-18', 'Compra papelería, carpetas, sellos y sobres'),
    ('Sueldos y salarios personal',       'Recursos Humanos', 45000.00, '2025-04-30', 'Planilla mensual 8 empleados abril 2025'),
]


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def init_db(db_path: str) -> None:
    """
    Inicializa la base de datos SQLite del sistema Acumatica ERP.

    Crea todas las tablas necesarias (si no existen) e inserta datos de ejemplo
    bolivianos realistas. La función es IDEMPOTENTE: verifica si ya hay datos
    antes de insertar, por lo que puede ejecutarse varias veces sin duplicar.

    Args:
        db_path (str): Ruta al archivo .db de SQLite (ej. 'acumatica.db').

    Returns:
        None
    """
    # Abrimos conexión al archivo de base de datos (se crea si no existe)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ── 1. Crear todas las tablas ──────────────────────────────────────────
    cursor.executescript(SQL_CREAR_TABLAS)
    conn.commit()

    # ── 2. Verificar si ya existen datos (idempotencia) ────────────────────
    total_clientes = cursor.execute('SELECT COUNT(*) FROM clientes').fetchone()[0]
    if total_clientes > 0:
        # La BD ya fue inicializada, no volvemos a insertar
        conn.close()
        return

    # ── 3. Insertar clientes ───────────────────────────────────────────────
    cursor.executemany(
        '''INSERT INTO clientes (nombre, empresa, email, telefono, ciudad, direccion, estado)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        SEED_CLIENTES
    )
    conn.commit()

    # ── 4. Insertar productos ──────────────────────────────────────────────
    cursor.executemany(
        '''INSERT INTO productos (nombre, descripcion, categoria, precio_unitario,
                                  stock, stock_minimo, unidad)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        SEED_PRODUCTOS
    )
    conn.commit()

    # ── 5. Insertar facturas e ítems ───────────────────────────────────────
    for factura in SEED_FACTURAS:
        numero, cliente_id, fecha_emision, fecha_vencimiento, descuento_pct, \
            estado, notas, items = factura

        # Calcular subtotal sumando todos los ítems de la factura
        subtotal = sum(cant * precio for _, _, cant, precio in items)

        # Aplicar descuento porcentual sobre el subtotal
        monto_descuento = subtotal * (descuento_pct / 100)
        total = subtotal - monto_descuento

        # Insertar cabecera de factura
        cursor.execute(
            '''INSERT INTO facturas
               (numero, cliente_id, fecha_emision, fecha_vencimiento,
                subtotal, descuento, total, estado, notas)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (numero, cliente_id, fecha_emision, fecha_vencimiento,
             subtotal, monto_descuento, total, estado, notas)
        )
        factura_id = cursor.lastrowid  # ID de la factura recién insertada

        # Insertar cada línea / ítem de la factura
        for producto_id, descripcion, cantidad, precio_unitario in items:
            subtotal_item = cantidad * precio_unitario
            cursor.execute(
                '''INSERT INTO factura_items
                   (factura_id, producto_id, descripcion, cantidad,
                    precio_unitario, subtotal)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (factura_id, producto_id, descripcion, cantidad,
                 precio_unitario, subtotal_item)
            )

    conn.commit()

    # ── 6. Insertar gastos ─────────────────────────────────────────────────
    cursor.executemany(
        '''INSERT INTO gastos (concepto, categoria, monto, fecha, descripcion)
           VALUES (?, ?, ?, ?, ?)''',
        SEED_GASTOS
    )
    conn.commit()

    # Cerramos la conexión al finalizar
    conn.close()
    print(f"[BD] Base de datos inicializada correctamente en: {db_path}")
    print(f"[BD]  - {len(SEED_CLIENTES)} clientes insertados")
    print(f"[BD]  - {len(SEED_PRODUCTOS)} productos insertados")
    print(f"[BD]  - {len(SEED_FACTURAS)} facturas insertadas")
    print(f"[BD]  - {len(SEED_GASTOS)} gastos insertados")
