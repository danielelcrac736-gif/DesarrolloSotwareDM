# 🏢 Acumatica ERP — Prototipo Web
**Proyecto Final · SIS-315 Sistemas de Gestión Empresarial · USFX 2025**
**Docente: Ing. Ricardo Quispe Requena**

---

## 📋 INSTRUCCIONES PARA CLAUDE CODE

Lee este README completo antes de escribir una sola línea de código.
Construye TODO lo que se describe aquí en una sola sesión, archivo por archivo.
No omitas ningún módulo. Cada archivo debe estar completamente implementado y funcional.

---

## 🎯 QUÉ ES ESTE PROYECTO

Prototipo web que simula un sistema ERP inspirado en Acumatica. Es una aplicación
Flask + SQLite con diseño oscuro moderno tipo dashboard profesional.
Debe verse y sentirse como un ERP real, con datos de ejemplo precargados.

**Objetivo académico:** Demostrar en la defensa que el grupo comprende cómo
funciona un ERP moderno, sus módulos, su arquitectura y su interfaz.

---

## 🗂️ ESTRUCTURA COMPLETA DE ARCHIVOS A CREAR

```
PROYECTO/
├── README.md                          ← este archivo
├── app.py                             ← servidor Flask principal
├── database.py                        ← inicialización y seed de BD
├── requirements.txt                   ← dependencias Python
├── run.bat                            ← script para Windows (doble clic)
│
├── templates/                         ← HTML con Jinja2
│   ├── base.html                      ← layout base con sidebar y navbar
│   ├── login.html                     ← pantalla de inicio de sesión
│   ├── dashboard.html                 ← página principal con KPIs y gráficos
│   ├── clientes.html                  ← listado + formulario de clientes
│   ├── cliente_detalle.html           ← detalle de un cliente específico
│   ├── inventario.html                ← listado de productos y stock
│   ├── contabilidad.html              ← facturas y movimientos financieros
│   ├── nueva_factura.html             ← formulario nueva factura
│   ├── reportes.html                  ← reportes con gráficos Chart.js
│   └── 404.html                       ← página de error
│
└── static/
    ├── css/
    │   └── style.css                  ← estilos globales dark theme
    ├── js/
    │   └── main.js                    ← JavaScript global (gráficos, tablas)
    └── img/
        └── logo.svg                   ← logo SVG inline de Acumatica (simplificado)
```

---

## ⚙️ STACK TECNOLÓGICO

| Capa | Tecnología | Por qué |
|------|-----------|---------|
| Backend | Python 3 + Flask | Simple, conocido, fácil de explicar |
| Base de datos | SQLite + sqlite3 nativo | Sin instalar servidor, archivo único |
| Frontend | HTML5 + CSS3 + Vanilla JS | Sin frameworks complejos |
| Gráficos | Chart.js (CDN) | Gráficos profesionales sin instalación |
| Íconos | Font Awesome 6 (CDN) | Íconos modernos sin instalación |
| Fuente | Inter (Google Fonts CDN) | Fuente profesional tipo SaaS |

---

## 🎨 DISEÑO — DARK THEME PROFESIONAL

### Paleta de colores (usar en style.css y en línea donde sea necesario)

```css
/* Variables CSS - definir en :root */
--bg-primary:     #0f1117;   /* fondo principal casi negro */
--bg-secondary:   #1a1d2e;   /* fondo sidebar y cards */
--bg-card:        #1e2235;   /* fondo de tarjetas */
--bg-hover:       #252840;   /* hover en elementos */
--accent:         #6c63ff;   /* morado principal Acumatica */
--accent-light:   #8b85ff;   /* variante clara del acento */
--accent-green:   #00d4aa;   /* verde para positivos/ganancias */
--accent-red:     #ff4757;   /* rojo para alertas/pérdidas */
--accent-yellow:  #ffa502;   /* amarillo para advertencias */
--accent-blue:    #1e90ff;   /* azul para información */
--text-primary:   #e8e8f0;   /* texto principal */
--text-secondary: #8b8fa8;   /* texto secundario/subtítulos */
--text-muted:     #5a5f7a;   /* texto deshabilitado */
--border:         #2a2d45;   /* bordes de cards y tablas */
--border-light:   #333655;   /* bordes más claros */
```

### Reglas de diseño a seguir
- Sidebar fijo a la izquierda, 240px de ancho
- Navbar superior con nombre de usuario y notificaciones
- Cards con `border-radius: 12px`, sombra sutil `box-shadow: 0 4px 20px rgba(0,0,0,0.3)`
- Tablas con fila hover en `--bg-hover`
- Botones principales con gradiente `linear-gradient(135deg, #6c63ff, #8b85ff)`
- Badges de estado con colores semánticos (verde=activo, rojo=inactivo, amarillo=pendiente)
- Inputs con fondo `#252840`, borde `--border`, texto `--text-primary`
- Transiciones suaves `transition: all 0.2s ease`
- Todo con `font-family: 'Inter', sans-serif`

---

## 🔐 MÓDULO: LOGIN

**Archivo:** `templates/login.html`

- Pantalla centrada, fondo `--bg-primary` con patrón de puntos CSS
- Logo "ACUMATICA ERP" con ícono de edificio
- Subtítulo "Sistema de Gestión Empresarial · USFX 2025"
- Campos: Usuario (ícono de persona) y Contraseña (ícono de candado)
- Botón "Iniciar Sesión" con gradiente accent
- Checkbox "Recordarme"
- Credenciales de demo visibles debajo: `admin / admin123`
- Mensaje de error si credenciales incorrectas (flash message)
- NO usar Flask-Login. Usar session['user'] directamente.

**Usuarios hardcodeados en app.py (dict):**
```python
USERS = {
    'admin':   {'password': 'admin123', 'nombre': 'Administrador',  'rol': 'Administrador'},
    'jhonn':   {'password': '1234',     'nombre': 'Jhonn Llanos',   'rol': 'Gerente'},
    'camila':  {'password': '1234',     'nombre': 'Camila Montecinos', 'rol': 'Contadora'},
    'erick':   {'password': '1234',     'nombre': 'Erick Arancibia', 'rol': 'Ventas'},
}
```

---

## 📊 MÓDULO: DASHBOARD

**Archivo:** `templates/dashboard.html`

### KPI Cards (fila superior) — 4 cards
Cada card tiene: ícono grande, valor principal, label, y comparación con mes anterior.

| Card | Valor ejemplo | Ícono | Color acento |
|------|--------------|-------|--------------|
| Ventas del Mes | Bs. 284,500 | fa-chart-line | --accent-green |
| Clientes Activos | 47 | fa-users | --accent |
| Facturas Pendientes | 12 | fa-file-invoice | --accent-yellow |
| Stock Bajo | 5 productos | fa-box-open | --accent-red |

### Gráfico 1 (izquierda, 60% ancho): Ventas últimos 6 meses
- Tipo: `Chart.js` — gráfico de área (line con fill)
- Color: gradiente de `--accent` a transparente
- Datos de ejemplo para 6 meses (Enero a Junio)
- Eje Y en Bolivianos (Bs.)

### Gráfico 2 (derecha, 40% ancho): Distribución por módulo
- Tipo: `Chart.js` — Doughnut
- Categorías: Ventas 40%, Manufactura 25%, Distribución 20%, Servicios 15%
- Colores: accent, accent-green, accent-blue, accent-yellow

### Tabla: Últimas 5 facturas (parte inferior)
- Columnas: #Factura, Cliente, Fecha, Monto, Estado
- Estado con badge de color (Pagada=verde, Pendiente=amarillo, Vencida=rojo)

### Tabla: Top 5 productos más vendidos (parte inferior derecha)
- Columnas: Producto, Categoría, Vendidos, Stock, Barra de progreso

---

## 👥 MÓDULO: CLIENTES / CRM

**Archivos:** `templates/clientes.html`, `templates/cliente_detalle.html`

### Tabla clientes con:
- Buscador en tiempo real (JavaScript, filtra sin recargar)
- Filtro por estado (Activo / Inactivo / Todos)
- Columnas: ID, Nombre, Empresa, Email, Teléfono, Ciudad, Estado, Acciones
- Acciones: Ver detalle (ícono ojo), Editar (ícono lápiz), Eliminar (ícono basura con confirm)
- Botón "Nuevo Cliente" que abre modal con formulario

### Modal "Nuevo Cliente" / "Editar Cliente":
Campos: Nombre completo, Empresa, Email, Teléfono, Ciudad, Dirección, Estado (select Activo/Inactivo)

### Detalle de cliente (`cliente_detalle.html`):
- Header con nombre, empresa y badges de estado
- Tabs: Información General | Facturas | Historial
- En "Facturas": listado de facturas asociadas a ese cliente
- Botón "Volver" y "Editar"

### Tabla `clientes` en SQLite:
```sql
CREATE TABLE clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    empresa TEXT,
    email TEXT,
    telefono TEXT,
    ciudad TEXT,
    direccion TEXT,
    estado TEXT DEFAULT 'Activo',
    fecha_registro TEXT DEFAULT (date('now'))
);
```

### Datos seed (mínimo 10 clientes bolivianos):
Empresas reales de Bolivia: Tigo Bolivia, YPFB, Banco BNB, Sofía Ltda,
Entel Bolivia, Farmacorp, Supermercados Ketal, CRE (Cooperativa Rural de Electrificación),
Fancesa, Cervecería Boliviana Nacional (CBN).

---

## 📦 MÓDULO: INVENTARIO

**Archivo:** `templates/inventario.html`

### Header con stats:
- Total productos, Valor total del inventario, Productos con stock bajo (<10), Categorías

### Filtros:
- Buscador por nombre
- Filtro por categoría (select)
- Filtro por estado de stock (Todos / Stock Normal / Stock Bajo / Sin Stock)

### Tabla de productos:
- Columnas: ID, Producto, Categoría, Precio Unit., Stock, Stock Mínimo, Estado, Acciones
- Estado del stock: badge verde (normal), amarillo (bajo), rojo (sin stock)
- Barra visual de stock (progreso relativo al stock mínimo)
- Acciones: Ver, Editar stock, Eliminar

### Modal "Nuevo Producto" / "Ajustar Stock":
Campos: Nombre, Descripción, Categoría, Precio Unitario, Stock Actual, Stock Mínimo, Unidad de medida

### Tabla `productos` en SQLite:
```sql
CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    categoria TEXT,
    precio_unitario REAL,
    stock INTEGER DEFAULT 0,
    stock_minimo INTEGER DEFAULT 10,
    unidad TEXT DEFAULT 'und',
    estado TEXT DEFAULT 'Activo',
    fecha_creacion TEXT DEFAULT (date('now'))
);
```

### Datos seed (mínimo 15 productos variados):
Mezcla de categorías: Tecnología, Oficina, Manufactura, Alimentos, Servicios.
Algunos con stock bajo para mostrar las alertas.

---

## 💰 MÓDULO: CONTABILIDAD

**Archivos:** `templates/contabilidad.html`, `templates/nueva_factura.html`

### Vista principal `contabilidad.html`:
- Stats row: Total Facturado, Cobrado, Pendiente, Vencido
- Tabs: Facturas | Gastos | Balance
- Tab "Facturas": tabla completa con filtros por fecha y estado
- Tab "Gastos": tabla de gastos registrados
- Tab "Balance": resumen Ingresos vs Egresos del mes actual

### Tabla de facturas:
- Columnas: #Factura, Cliente, Fecha Emisión, Fecha Vencimiento, Monto, Estado, Acciones
- Botón "Nueva Factura" → va a `nueva_factura.html`
- Botón "Marcar como Pagada" (cambia estado sin recargar, fetch API)
- Descarga PDF simulada (botón que muestra alert "Generando PDF...")

### Formulario `nueva_factura.html`:
- Selector de cliente (dropdown con clientes de BD)
- Tabla dinámica de ítems: agregar/quitar líneas con JS
  - Cada línea: Producto (dropdown), Cantidad, Precio Unit., Subtotal (calculado automático)
- Campos: Fecha emisión, Fecha vencimiento, Notas, Descuento %
- Total calculado en tiempo real con JS
- Botón "Guardar Factura" y "Cancelar"

### Tablas SQLite:
```sql
CREATE TABLE facturas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT UNIQUE,
    cliente_id INTEGER,
    fecha_emision TEXT,
    fecha_vencimiento TEXT,
    subtotal REAL,
    descuento REAL DEFAULT 0,
    total REAL,
    estado TEXT DEFAULT 'Pendiente',
    notas TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

CREATE TABLE factura_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    factura_id INTEGER,
    producto_id INTEGER,
    descripcion TEXT,
    cantidad INTEGER,
    precio_unitario REAL,
    subtotal REAL,
    FOREIGN KEY (factura_id) REFERENCES facturas(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

CREATE TABLE gastos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    concepto TEXT NOT NULL,
    categoria TEXT,
    monto REAL,
    fecha TEXT,
    descripcion TEXT
);
```

### Datos seed: mínimo 15 facturas y 10 gastos con distintos estados.

---

## 📈 MÓDULO: REPORTES

**Archivo:** `templates/reportes.html`

### 4 gráficos en grid 2x2:

**Gráfico 1 — Ventas por Mes (Bar Chart):**
- 12 meses, barras con gradiente accent
- Eje Y en Bolivianos

**Gráfico 2 — Clientes por Ciudad (Horizontal Bar):**
- Top 6 ciudades: Sucre, La Paz, Cochabamba, Santa Cruz, Oruro, Potosí
- Color accent-green

**Gráfico 3 — Estado de Facturas (Pie Chart):**
- Pagadas, Pendientes, Vencidas
- Colores: verde, amarillo, rojo

**Gráfico 4 — Productos por Categoría (Doughnut):**
- Tecnología, Oficina, Manufactura, Alimentos, Servicios
- Paleta multicolor

### Tabla de resumen ejecutivo:
- KPIs del año: Mejor mes, Peor mes, Promedio mensual, Total anual
- Exportar a CSV (botón que genera y descarga el CSV con JS)

---

## 🔧 ARCHIVO: app.py

```python
# Estructura esperada de app.py — implementar completo

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from datetime import datetime, date
from database import init_db

app = Flask(__name__)
app.secret_key = 'acumatica_usfx_2025_sis315'

DB_PATH = 'acumatica.db'

USERS = {
    'admin':  {'password': 'admin123', 'nombre': 'Administrador',     'rol': 'Administrador'},
    'jhonn':  {'password': '1234',     'nombre': 'Jhonn Llanos',      'rol': 'Gerente'},
    'camila': {'password': '1234',     'nombre': 'Camila Montecinos', 'rol': 'Contadora'},
    'erick':  {'password': '1234',     'nombre': 'Erick Arancibia',   'rol': 'Ventas'},
}

def get_db():
    """Retorna conexión a SQLite con row_factory para dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    """Decorador para proteger rutas."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# RUTAS A IMPLEMENTAR:
# GET/POST /login
# GET      /logout
# GET      /  → dashboard (login_required)
# GET      /clientes
# POST     /clientes/nuevo
# GET      /clientes/<id>
# POST     /clientes/<id>/editar
# POST     /clientes/<id>/eliminar
# GET      /inventario
# POST     /inventario/nuevo
# POST     /inventario/<id>/editar
# POST     /inventario/<id>/eliminar
# GET      /contabilidad
# GET/POST /contabilidad/nueva-factura
# POST     /contabilidad/factura/<id>/pagar  (API JSON)
# GET      /reportes
# GET      /api/dashboard-data              (retorna JSON para gráficos)

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        init_db(DB_PATH)
        print("Base de datos creada con datos de ejemplo.")
    app.run(debug=True, port=5000)
```

---

## 🔧 ARCHIVO: database.py

Debe contener la función `init_db(db_path)` que:
1. Crea todas las tablas (si no existen)
2. Inserta datos seed completos (clientes, productos, facturas, gastos)
3. Es idempotente (puede correrse varias veces sin duplicar datos)

Los datos seed deben ser **realistas y bolivianos**: nombres, ciudades (Sucre, La Paz, Cbba, SCZ), montos en Bolivianos (Bs.), productos relevantes para empresas latinoamericanas.

---

## 🔧 ARCHIVO: requirements.txt

```
flask==3.0.3
```
Solo Flask. Todo lo demás (sqlite3, datetime, os) es librería estándar de Python.

---

## 🔧 ARCHIVO: run.bat

```bat
@echo off
echo Iniciando Acumatica ERP Prototipo...
echo.
pip install flask -q
python app.py
pause
```

---

## 🔧 ARCHIVO: static/css/style.css

CSS global con:
- Variables CSS en `:root` (toda la paleta definida arriba)
- Reset básico (`*, box-sizing: border-box`, margin/padding 0)
- Estilos del layout: sidebar fijo, main-content con margin-left
- Estilos de navbar superior
- Estilos de cards KPI
- Estilos de tablas (thead oscuro, hover, badges)
- Estilos de formularios y modales
- Estilos de botones (primary, secondary, danger, success)
- Estilos de alerts/flash messages
- Responsive básico (sidebar colapsable en móvil)
- Animaciones de entrada para cards (`@keyframes fadeInUp`)
- Scrollbar personalizado (oscuro)

---

## 🔧 ARCHIVO: static/js/main.js

JavaScript global con:
- Función `initDataTable(tableId)` para búsqueda en tiempo real en tablas
- Función `showModal(modalId)` y `closeModal(modalId)`
- Función `confirmDelete(url, nombre)` con confirm() nativo
- Función `formatCurrency(amount)` → "Bs. 1,234.50"
- Función `showAlert(message, type)` para flash messages dinámicos
- Listeners para cerrar modal al hacer clic fuera
- Auto-dismiss de flash messages a los 4 segundos
- Para nueva factura: cálculo automático de subtotales y total

---

## 📝 COMENTARIOS EN EL CÓDIGO

**MUY IMPORTANTE:** Todo el código debe estar bien comentado en español.
Cada función debe tener un docstring explicando qué hace, qué recibe y qué retorna.
Los bloques importantes deben tener comentario de una línea.
El propósito es que cualquier integrante pueda explicar el código en la defensa.

Ejemplo de nivel de comentario esperado:
```python
def get_clientes():
    """
    Obtiene todos los clientes de la base de datos.
    Retorna una lista de diccionarios con los datos de cada cliente.
    Se conecta a SQLite, ejecuta SELECT y cierra la conexión.
    """
    conn = get_db()
    # Consulta todos los clientes ordenados por nombre
    clientes = conn.execute('SELECT * FROM clientes ORDER BY nombre').fetchall()
    conn.close()
    return clientes
```

---

## ✅ CHECKLIST FINAL — ANTES DE TERMINAR

Verificar que todo esto funciona:

- [ ] `python app.py` inicia sin errores
- [ ] `http://localhost:5000` muestra login
- [ ] Login con `admin / admin123` funciona
- [ ] Dashboard muestra KPIs y gráficos
- [ ] Clientes: listar, crear, editar, eliminar, ver detalle
- [ ] Inventario: listar, crear, editar stock, filtrar por categoría
- [ ] Contabilidad: listar facturas, crear nueva factura con ítems, marcar como pagada
- [ ] Reportes: 4 gráficos visibles con datos
- [ ] Logout funciona y redirige a login
- [ ] No hay errores en consola del navegador
- [ ] El diseño se ve profesional y oscuro en Chrome/Edge

---

## 🚀 PROMPT PARA CLAUDE CODE

Cuando tengas este README, dale este prompt a Claude Code:

```
Lee el README.md completo y construye el proyecto Acumatica ERP Prototipo 
exactamente como está especificado. Crea todos los archivos listados en la 
estructura de carpetas. El código debe estar completamente funcional, bien 
comentado en español, con diseño oscuro profesional usando la paleta de 
colores definida. Empieza por database.py, luego app.py, luego style.css, 
luego los templates en orden: base.html, login.html, dashboard.html, 
clientes.html, cliente_detalle.html, inventario.html, contabilidad.html, 
nueva_factura.html, reportes.html. Finalmente main.js y los archivos de 
soporte. No te detengas hasta completar todos los archivos.
```

---

*SIS-315 · USFX Sucre · 2025 · Grupo: Aillón, Montecinos, Villegas, Aguilar, Llanos, Villarroel, Arancibia, Mamani, Marquez, Lazaro*
