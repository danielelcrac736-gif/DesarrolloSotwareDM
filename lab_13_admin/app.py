"""
app.py — Servidor principal Flask del sistema Acumatica ERP
Proyecto Final · SIS-315 Sistemas de Gestión Empresarial · USFX 2025
Grupo: Aillón, Montecinos, Villegas, Aguilar, Llanos, Villarroel,
       Arancibia, Mamani, Marquez, Lazaro

Define la aplicación Flask, todas las rutas de los módulos, la autenticación
por sesión (sin Flask-Login), y los endpoints JSON para los gráficos Chart.js.
"""

from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, jsonify)
import sqlite3
import os
import json
from datetime import date
from functools import wraps
from database import init_db


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE LA APLICACIÓN
# ─────────────────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = 'acumatica_usfx_2025_sis315'   # Firma las cookies de sesión

DB_PATH = 'acumatica.db'   # Archivo SQLite (se crea en el mismo directorio)

# Usuarios del sistema hardcodeados (en producción estarían en BD con hash)
USERS = {
    'admin':  {'password': 'admin123', 'nombre': 'Administrador',     'rol': 'Administrador'},
    'jhonn':  {'password': '1234',     'nombre': 'Jhonn Llanos',      'rol': 'Gerente'},
    'camila': {'password': '1234',     'nombre': 'Camila Montecinos', 'rol': 'Contadora'},
    'erick':  {'password': '1234',     'nombre': 'Erick Arancibia',   'rol': 'Ventas'},
}


# ─────────────────────────────────────────────────────────────────────────────
# UTILIDADES: BASE DE DATOS Y AUTENTICACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def get_db():
    """
    Abre y retorna una conexión a la base de datos SQLite.

    Configura row_factory = sqlite3.Row para que cada fila se comporte
    como un diccionario: se puede acceder a las columnas por nombre
    (ej. fila['nombre']) en lugar de por índice numérico.

    Returns:
        sqlite3.Connection: Conexión lista para ejecutar consultas.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # Acceso por nombre de columna
    return conn


def login_required(f):
    """
    Decorador para proteger rutas que requieren sesión iniciada.

    Si el usuario no está autenticado (no existe 'user' en session),
    lo redirige al login con un mensaje flash de advertencia.

    Args:
        f: Función de vista a proteger.

    Returns:
        Función decorada que verifica la sesión antes de ejecutar.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULO: AUTENTICACIÓN (Login / Logout)
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Muestra el formulario de inicio de sesión (GET) y procesa las
    credenciales enviadas (POST).

    Si las credenciales coinciden con USERS, guarda el usuario en session
    y redirige al dashboard. Si son incorrectas, muestra un mensaje de
    error vía flash y vuelve al formulario.

    Returns:
        GET : Renderiza templates/login.html
        POST: Redirige a / (dashboard) si el login es exitoso,
              o vuelve a login.html con mensaje de error.
    """
    # Si ya tiene sesión activa, ir directo al dashboard
    if 'user' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '').strip()

        # Verificar credenciales contra el diccionario de usuarios
        if username in USERS and USERS[username]['password'] == password:
            session['user']   = username
            session['nombre'] = USERS[username]['nombre']
            session['rol']    = USERS[username]['rol']
            flash(f"Bienvenido de nuevo, {USERS[username]['nombre']}.", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos. Verifica e intenta de nuevo.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """
    Cierra la sesión activa eliminando todos los datos almacenados en
    session y redirige al formulario de login.

    Returns:
        Redirige a /login con mensaje informativo.
    """
    session.clear()
    flash('Sesión cerrada correctamente. ¡Hasta pronto!', 'info')
    return redirect(url_for('login'))


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULO: DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/')
@login_required
def dashboard():
    """
    Página principal del ERP. Muestra 4 tarjetas KPI, gráficos y
    tablas resumen con los datos más recientes del sistema.

    KPIs calculados en tiempo real:
    - Ventas del mes : suma de facturas pagadas en el mes actual (Bs.)
    - Clientes activos: conteo de clientes con estado = 'Activo'
    - Facturas pendientes: conteo de facturas sin cobrar
    - Stock bajo: productos cuyo stock < stock_minimo

    Tablas de resumen:
    - Últimas 5 facturas emitidas (con cliente y estado)
    - Top 5 productos más vendidos por cantidad

    Returns:
        Renderiza templates/dashboard.html con todos los datos.
    """
    conn = get_db()
    mes_actual = date.today().strftime('%Y-%m')   # Ej.: '2025-05'

    # ── KPI 1: Ventas del mes (facturas pagadas este mes) ──────────────────
    ventas_mes = conn.execute(
        """SELECT COALESCE(SUM(total), 0) AS total
           FROM facturas
           WHERE fecha_emision LIKE ? AND estado = 'Pagada'""",
        (f'{mes_actual}%',)
    ).fetchone()['total']

    # ── KPI 2: Clientes activos ────────────────────────────────────────────
    clientes_activos = conn.execute(
        "SELECT COUNT(*) AS total FROM clientes WHERE estado = 'Activo'"
    ).fetchone()['total']

    # ── KPI 3: Facturas pendientes de cobro ────────────────────────────────
    facturas_pendientes = conn.execute(
        "SELECT COUNT(*) AS total FROM facturas WHERE estado = 'Pendiente'"
    ).fetchone()['total']

    # ── KPI 4: Productos con stock por debajo del mínimo ──────────────────
    stock_bajo = conn.execute(
        """SELECT COUNT(*) AS total
           FROM productos
           WHERE stock < stock_minimo AND estado = 'Activo'"""
    ).fetchone()['total']

    # ── Últimas 5 facturas con nombre del cliente ──────────────────────────
    ultimas_facturas = conn.execute(
        """SELECT f.numero, f.fecha_emision, f.total, f.estado,
                  c.nombre AS cliente_nombre
           FROM facturas f
           JOIN clientes c ON f.cliente_id = c.id
           ORDER BY f.id DESC
           LIMIT 5"""
    ).fetchall()

    # ── Top 5 productos por cantidad vendida (suma de ítems en facturas) ──
    top_productos = conn.execute(
        """SELECT p.nombre, p.categoria, p.stock, p.stock_minimo,
                  COALESCE(SUM(fi.cantidad), 0) AS vendidos
           FROM productos p
           LEFT JOIN factura_items fi ON p.id = fi.producto_id
           GROUP BY p.id
           ORDER BY vendidos DESC
           LIMIT 5"""
    ).fetchall()

    conn.close()

    return render_template('dashboard.html',
                           ventas_mes=ventas_mes,
                           clientes_activos=clientes_activos,
                           facturas_pendientes=facturas_pendientes,
                           stock_bajo=stock_bajo,
                           ultimas_facturas=ultimas_facturas,
                           top_productos=top_productos)


@app.route('/api/dashboard-data')
@login_required
def api_dashboard_data():
    """
    Endpoint de API que retorna datos JSON para los gráficos del dashboard.

    Gráfico 1 (línea/área): ventas reales de los últimos 6 meses obtenidas
    de la tabla facturas (cualquier estado).

    Gráfico 2 (doughnut): distribución por módulo ERP (valores fijos
    representativos para la demo, según el README).

    Returns:
        JSON con las siguientes claves:
        - etiquetas_meses   : lista de 6 nombres de mes
        - ventas_6meses     : lista de 6 totales en Bs.
        - distribucion_labels: etiquetas del doughnut
        - distribucion_valores: valores porcentuales del doughnut
    """
    conn = get_db()
    hoy = date.today()

    nombres_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                     'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

    ventas_meses   = []
    etiquetas_meses = []

    # Calcular ventas mes a mes retrocediendo 5 meses desde hoy
    for i in range(5, -1, -1):
        mes_num = hoy.month - i
        año_num = hoy.year
        if mes_num <= 0:
            mes_num += 12
            año_num -= 1

        prefijo = f'{año_num}-{mes_num:02d}'
        etiquetas_meses.append(nombres_meses[mes_num - 1])

        total = conn.execute(
            "SELECT COALESCE(SUM(total), 0) AS t FROM facturas WHERE fecha_emision LIKE ?",
            (f'{prefijo}%',)
        ).fetchone()['t']
        ventas_meses.append(round(total, 2))

    conn.close()

    # Distribución por módulo (fija para la demo, tal como indica el README)
    distribucion_labels  = ['Ventas', 'Manufactura', 'Distribución', 'Servicios']
    distribucion_valores = [40, 25, 20, 15]

    return jsonify({
        'etiquetas_meses':      etiquetas_meses,
        'ventas_6meses':        ventas_meses,
        'distribucion_labels':  distribucion_labels,
        'distribucion_valores': distribucion_valores,
    })


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULO: CLIENTES / CRM
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/clientes')
@login_required
def clientes():
    """
    Lista todos los clientes registrados en el sistema, ordenados por nombre.

    Returns:
        Renderiza templates/clientes.html con la lista completa.
    """
    conn = get_db()
    lista = conn.execute(
        'SELECT * FROM clientes ORDER BY nombre'
    ).fetchall()
    conn.close()
    return render_template('clientes.html', clientes=lista)


@app.route('/clientes/nuevo', methods=['POST'])
@login_required
def cliente_nuevo():
    """
    Crea un nuevo cliente con los datos enviados desde el formulario modal.

    Campos requeridos: nombre
    Campos opcionales: empresa, email, telefono, ciudad, direccion, estado

    Returns:
        Redirige a /clientes con mensaje de éxito o error.
    """
    nombre    = request.form.get('nombre',    '').strip()
    empresa   = request.form.get('empresa',   '').strip()
    email     = request.form.get('email',     '').strip()
    telefono  = request.form.get('telefono',  '').strip()
    ciudad    = request.form.get('ciudad',    '').strip()
    direccion = request.form.get('direccion', '').strip()
    estado    = request.form.get('estado',    'Activo')

    if not nombre:
        flash('El nombre del cliente es obligatorio.', 'danger')
        return redirect(url_for('clientes'))

    conn = get_db()
    conn.execute(
        '''INSERT INTO clientes
           (nombre, empresa, email, telefono, ciudad, direccion, estado)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (nombre, empresa, email, telefono, ciudad, direccion, estado)
    )
    conn.commit()
    conn.close()

    flash(f'Cliente "{nombre}" registrado correctamente.', 'success')
    return redirect(url_for('clientes'))


@app.route('/clientes/<int:id>')
@login_required
def cliente_detalle(id):
    """
    Muestra la ficha completa de un cliente: datos generales y sus facturas.

    Args:
        id (int): ID del cliente en la base de datos.

    Returns:
        Renderiza templates/cliente_detalle.html, o 404 si no existe.
    """
    conn = get_db()

    cliente = conn.execute(
        'SELECT * FROM clientes WHERE id = ?', (id,)
    ).fetchone()

    if not cliente:
        conn.close()
        return render_template('404.html'), 404

    # Historial de facturas asociadas al cliente
    facturas_cliente = conn.execute(
        """SELECT id, numero, fecha_emision, fecha_vencimiento, total, estado
           FROM facturas
           WHERE cliente_id = ?
           ORDER BY fecha_emision DESC""",
        (id,)
    ).fetchall()

    conn.close()
    return render_template('cliente_detalle.html',
                           cliente=cliente,
                           facturas=facturas_cliente)


@app.route('/clientes/<int:id>/editar', methods=['POST'])
@login_required
def cliente_editar(id):
    """
    Actualiza los datos de un cliente existente.

    Recibe los nuevos valores desde el formulario modal de edición (POST).

    Args:
        id (int): ID del cliente a actualizar.

    Returns:
        Redirige a /clientes con mensaje de resultado.
    """
    nombre    = request.form.get('nombre',    '').strip()
    empresa   = request.form.get('empresa',   '').strip()
    email     = request.form.get('email',     '').strip()
    telefono  = request.form.get('telefono',  '').strip()
    ciudad    = request.form.get('ciudad',    '').strip()
    direccion = request.form.get('direccion', '').strip()
    estado    = request.form.get('estado',    'Activo')

    if not nombre:
        flash('El nombre del cliente es obligatorio.', 'danger')
        return redirect(url_for('clientes'))

    conn = get_db()
    conn.execute(
        '''UPDATE clientes
           SET nombre=?, empresa=?, email=?, telefono=?,
               ciudad=?, direccion=?, estado=?
           WHERE id=?''',
        (nombre, empresa, email, telefono, ciudad, direccion, estado, id)
    )
    conn.commit()
    conn.close()

    flash(f'Cliente "{nombre}" actualizado correctamente.', 'success')
    return redirect(url_for('clientes'))


@app.route('/clientes/<int:id>/eliminar', methods=['POST'])
@login_required
def cliente_eliminar(id):
    """
    Elimina un cliente del sistema si no tiene facturas asociadas.

    Si el cliente tiene facturas, se rechaza la eliminación para mantener
    la integridad referencial de los datos históricos.

    Args:
        id (int): ID del cliente a eliminar.

    Returns:
        Redirige a /clientes con mensaje de resultado.
    """
    conn = get_db()

    cliente = conn.execute(
        'SELECT nombre FROM clientes WHERE id = ?', (id,)
    ).fetchone()

    if not cliente:
        conn.close()
        flash('Cliente no encontrado.', 'danger')
        return redirect(url_for('clientes'))

    # Proteger integridad: no borrar si tiene facturas
    facturas_count = conn.execute(
        'SELECT COUNT(*) AS total FROM facturas WHERE cliente_id = ?', (id,)
    ).fetchone()['total']

    if facturas_count > 0:
        conn.close()
        flash(f'No se puede eliminar: el cliente tiene {facturas_count} '
              f'factura(s) asociada(s). Desactívalo en su lugar.', 'warning')
        return redirect(url_for('clientes'))

    nombre = cliente['nombre']
    conn.execute('DELETE FROM clientes WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash(f'Cliente "{nombre}" eliminado correctamente.', 'success')
    return redirect(url_for('clientes'))


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULO: INVENTARIO
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/inventario')
@login_required
def inventario():
    """
    Lista todos los productos del inventario junto con estadísticas globales.

    Estadísticas calculadas:
    - total_productos : número de productos activos
    - valor_total     : suma de (precio_unitario * stock) de todos los activos
    - stock_bajo      : productos activos con stock < stock_minimo
    - num_categorias  : categorías únicas de productos activos

    Returns:
        Renderiza templates/inventario.html con productos, stats y categorías.
    """
    conn = get_db()

    productos = conn.execute(
        'SELECT * FROM productos ORDER BY categoria, nombre'
    ).fetchall()

    # Estadísticas del panel superior
    stats = conn.execute(
        """SELECT
            COUNT(*) AS total_productos,
            COALESCE(SUM(precio_unitario * stock), 0) AS valor_total,
            SUM(CASE WHEN stock < stock_minimo THEN 1 ELSE 0 END) AS stock_bajo,
            COUNT(DISTINCT categoria) AS num_categorias
           FROM productos
           WHERE estado = 'Activo'"""
    ).fetchone()

    # Categorías únicas para el filtro desplegable
    categorias = conn.execute(
        'SELECT DISTINCT categoria FROM productos ORDER BY categoria'
    ).fetchall()

    conn.close()
    return render_template('inventario.html',
                           productos=productos,
                           stats=stats,
                           categorias=categorias)


@app.route('/inventario/nuevo', methods=['POST'])
@login_required
def inventario_nuevo():
    """
    Registra un nuevo producto en el inventario.

    Campos requeridos: nombre
    Campos opcionales: descripcion, categoria, precio_unitario,
                       stock, stock_minimo, unidad

    Returns:
        Redirige a /inventario con mensaje de resultado.
    """
    nombre          = request.form.get('nombre',          '').strip()
    descripcion     = request.form.get('descripcion',     '').strip()
    categoria       = request.form.get('categoria',       '').strip()
    precio_unitario = request.form.get('precio_unitario', 0)
    stock           = request.form.get('stock',           0)
    stock_minimo    = request.form.get('stock_minimo',    10)
    unidad          = request.form.get('unidad',          'und').strip()

    if not nombre:
        flash('El nombre del producto es obligatorio.', 'danger')
        return redirect(url_for('inventario'))

    try:
        precio_unitario = float(precio_unitario)
        stock           = int(stock)
        stock_minimo    = int(stock_minimo)
    except (ValueError, TypeError):
        flash('Los valores de precio y stock deben ser numéricos.', 'danger')
        return redirect(url_for('inventario'))

    conn = get_db()
    conn.execute(
        '''INSERT INTO productos
           (nombre, descripcion, categoria, precio_unitario, stock, stock_minimo, unidad)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (nombre, descripcion, categoria, precio_unitario, stock, stock_minimo, unidad)
    )
    conn.commit()
    conn.close()

    flash(f'Producto "{nombre}" agregado al inventario.', 'success')
    return redirect(url_for('inventario'))


@app.route('/inventario/<int:id>/editar', methods=['POST'])
@login_required
def inventario_editar(id):
    """
    Actualiza los datos de un producto existente, incluido el ajuste de stock.

    Args:
        id (int): ID del producto a modificar.

    Returns:
        Redirige a /inventario con mensaje de resultado.
    """
    nombre          = request.form.get('nombre',          '').strip()
    descripcion     = request.form.get('descripcion',     '').strip()
    categoria       = request.form.get('categoria',       '').strip()
    precio_unitario = request.form.get('precio_unitario', 0)
    stock           = request.form.get('stock',           0)
    stock_minimo    = request.form.get('stock_minimo',    10)
    unidad          = request.form.get('unidad',          'und').strip()

    if not nombre:
        flash('El nombre del producto es obligatorio.', 'danger')
        return redirect(url_for('inventario'))

    try:
        precio_unitario = float(precio_unitario)
        stock           = int(stock)
        stock_minimo    = int(stock_minimo)
    except (ValueError, TypeError):
        flash('Los valores de precio y stock deben ser numéricos.', 'danger')
        return redirect(url_for('inventario'))

    conn = get_db()
    conn.execute(
        '''UPDATE productos
           SET nombre=?, descripcion=?, categoria=?, precio_unitario=?,
               stock=?, stock_minimo=?, unidad=?
           WHERE id=?''',
        (nombre, descripcion, categoria, precio_unitario,
         stock, stock_minimo, unidad, id)
    )
    conn.commit()
    conn.close()

    flash(f'Producto "{nombre}" actualizado correctamente.', 'success')
    return redirect(url_for('inventario'))


@app.route('/inventario/<int:id>/eliminar', methods=['POST'])
@login_required
def inventario_eliminar(id):
    """
    Elimina un producto del inventario. Si el producto aparece en facturas
    históricas, se desactiva en lugar de borrar para preservar la integridad
    de los datos contables.

    Args:
        id (int): ID del producto a eliminar o desactivar.

    Returns:
        Redirige a /inventario con mensaje de resultado.
    """
    conn = get_db()

    producto = conn.execute(
        'SELECT nombre FROM productos WHERE id = ?', (id,)
    ).fetchone()

    if not producto:
        conn.close()
        flash('Producto no encontrado.', 'danger')
        return redirect(url_for('inventario'))

    nombre = producto['nombre']

    # Verificar si aparece en ítems de facturas históricas
    en_facturas = conn.execute(
        'SELECT COUNT(*) AS total FROM factura_items WHERE producto_id = ?', (id,)
    ).fetchone()['total']

    if en_facturas > 0:
        # Desactivar en lugar de borrar: mantiene la historia contable intacta
        conn.execute("UPDATE productos SET estado = 'Inactivo' WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        flash(f'Producto "{nombre}" desactivado (tiene {en_facturas} '
              f'registro(s) en facturas históricas).', 'warning')
    else:
        conn.execute('DELETE FROM productos WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        flash(f'Producto "{nombre}" eliminado correctamente.', 'success')

    return redirect(url_for('inventario'))


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULO: CONTABILIDAD
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/contabilidad')
@login_required
def contabilidad():
    """
    Vista principal del módulo contable con tres pestañas:
    Facturas, Gastos y Balance del mes corriente.

    Estadísticas del panel superior (históricas, todas las facturas):
    - total_facturado : suma de todos los totales
    - total_cobrado   : suma de facturas con estado 'Pagada'
    - total_pendiente : suma de facturas con estado 'Pendiente'
    - total_vencido   : suma de facturas con estado 'Vencida'

    Balance del mes actual:
    - ingresos_mes : facturas pagadas en el mes actual
    - egresos_mes  : gastos registrados en el mes actual
    - balance_mes  : ingresos_mes - egresos_mes

    Returns:
        Renderiza templates/contabilidad.html con todos los datos.
    """
    conn = get_db()
    mes_actual = date.today().strftime('%Y-%m')

    # Estadísticas globales de facturas (renombrado a stats_row para convertir después)
    stats_row = conn.execute(
        """SELECT
            COALESCE(SUM(total), 0) AS total_facturado,
            COALESCE(SUM(CASE WHEN estado = 'Pagada'    THEN total ELSE 0 END), 0) AS total_cobrado,
            COALESCE(SUM(CASE WHEN estado = 'Pendiente' THEN total ELSE 0 END), 0) AS total_pendiente,
            COALESCE(SUM(CASE WHEN estado = 'Vencida'   THEN total ELSE 0 END), 0) AS total_vencido
           FROM facturas"""
    ).fetchone()

    # Lista completa de facturas con el nombre del cliente
    facturas = conn.execute(
        """SELECT f.*, c.nombre AS cliente_nombre
           FROM facturas f
           JOIN clientes c ON f.cliente_id = c.id
           ORDER BY f.id DESC"""
    ).fetchall()

    # Lista de gastos del más reciente al más antiguo
    gastos = conn.execute(
        'SELECT * FROM gastos ORDER BY fecha DESC'
    ).fetchall()

    # Ingresos del mes actual (facturas pagadas)
    ingresos_mes = conn.execute(
        """SELECT COALESCE(SUM(total), 0) AS total
           FROM facturas
           WHERE fecha_emision LIKE ? AND estado = 'Pagada'""",
        (f'{mes_actual}%',)
    ).fetchone()['total']

    # Egresos del mes actual (gastos registrados)
    egresos_mes = conn.execute(
        "SELECT COALESCE(SUM(monto), 0) AS total FROM gastos WHERE fecha LIKE ?",
        (f'{mes_actual}%',)
    ).fetchone()['total']

    conn.close()

    # Consolidar todo en un dict plano; or 0 protege contra None residual de SQLite
    stats = {
        'total_facturado': stats_row['total_facturado'] or 0,
        'total_cobrado':   stats_row['total_cobrado']   or 0,
        'total_pendiente': stats_row['total_pendiente'] or 0,
        'total_vencido':   stats_row['total_vencido']   or 0,
        'ingresos_mes':    ingresos_mes or 0,
        'egresos_mes':     egresos_mes  or 0,
    }

    return render_template('contabilidad.html',
                           stats=stats,
                           facturas=facturas,
                           gastos=gastos,
                           balance_mes=stats['ingresos_mes'] - stats['egresos_mes'])


@app.route('/contabilidad/nueva-factura', methods=['GET', 'POST'])
@login_required
def nueva_factura():
    """
    Muestra el formulario de nueva factura (GET) y la procesa (POST).

    GET: Carga los dropdowns de clientes activos y productos activos.

    POST: Procesa la factura con sus ítems dinámicos.
    - Genera número de factura automático: FAC-AAAA-NNN
    - Lee ítems con claves producto_id_1, cantidad_1, precio_1, descripcion_1 ...
    - Calcula subtotales por ítem y aplica descuento porcentual al total
    - Inserta en tablas 'facturas' y 'factura_items'
    - Redirige a /contabilidad con mensaje de resultado

    Returns:
        GET : Renderiza templates/nueva_factura.html
        POST: Redirige a /contabilidad con flash de resultado.
    """
    conn = get_db()

    if request.method == 'GET':
        clientes_activos = conn.execute(
            "SELECT id, nombre, empresa FROM clientes WHERE estado = 'Activo' ORDER BY nombre"
        ).fetchall()
        productos_activos = conn.execute(
            "SELECT id, nombre, precio_unitario FROM productos WHERE estado = 'Activo' ORDER BY nombre"
        ).fetchall()
        conn.close()
        return render_template('nueva_factura.html',
                               clientes=clientes_activos,
                               productos=productos_activos)

    # ── Procesar el POST ───────────────────────────────────────────────────
    cliente_id        = request.form.get('cliente_id', '').strip()
    fecha_emision     = request.form.get('fecha_emision',    date.today().isoformat())
    fecha_vencimiento = request.form.get('fecha_vencimiento', '')
    descuento_pct     = float(request.form.get('descuento', 0) or 0)
    notas             = request.form.get('notas', '').strip()

    if not cliente_id:
        flash('Debes seleccionar un cliente para la factura.', 'danger')
        conn.close()
        return redirect(url_for('nueva_factura'))

    # Recoger ítems dinámicos del formulario
    # El frontend envía: producto_id_1, descripcion_1, cantidad_1, precio_1,
    #                    producto_id_2, descripcion_2, cantidad_2, precio_2 ...
    items = []
    idx = 1
    while True:
        prod_id = request.form.get(f'producto_id_{idx}')
        if prod_id is None:
            break   # No hay más filas de ítems
        try:
            cantidad    = int(request.form.get(f'cantidad_{idx}',    1))
            precio      = float(request.form.get(f'precio_{idx}',    0))
            descripcion = request.form.get(f'descripcion_{idx}', '').strip()
            if prod_id and cantidad > 0 and precio > 0:
                items.append((int(prod_id), descripcion, cantidad, precio))
        except (ValueError, TypeError):
            pass   # Ignorar filas con datos inválidos
        idx += 1

    if not items:
        flash('La factura debe tener al menos un ítem con cantidad y precio.', 'danger')
        conn.close()
        return redirect(url_for('nueva_factura'))

    # Calcular totales de la factura
    subtotal         = sum(cant * precio for _, _, cant, precio in items)
    monto_descuento  = subtotal * (descuento_pct / 100)
    total            = subtotal - monto_descuento

    # Generar número de factura: FAC-2025-001, FAC-2025-002 ...
    año_actual  = date.today().year
    count_año   = conn.execute(
        "SELECT COUNT(*) AS total FROM facturas WHERE numero LIKE ?",
        (f'FAC-{año_actual}-%',)
    ).fetchone()['total']
    numero_fac = f'FAC-{año_actual}-{count_año + 1:03d}'

    # Insertar cabecera de la factura
    cursor = conn.execute(
        """INSERT INTO facturas
           (numero, cliente_id, fecha_emision, fecha_vencimiento,
            subtotal, descuento, total, estado, notas)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'Pendiente', ?)""",
        (numero_fac, cliente_id, fecha_emision, fecha_vencimiento,
         subtotal, monto_descuento, total, notas)
    )
    factura_id = cursor.lastrowid   # ID de la factura recién creada

    # Insertar líneas de detalle de la factura
    for prod_id, descripcion, cantidad, precio in items:
        conn.execute(
            """INSERT INTO factura_items
               (factura_id, producto_id, descripcion, cantidad, precio_unitario, subtotal)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (factura_id, prod_id, descripcion, cantidad, precio, cantidad * precio)
        )

    conn.commit()
    conn.close()

    flash(f'Factura {numero_fac} creada exitosamente por Bs. {total:,.2f}.', 'success')
    return redirect(url_for('contabilidad'))


@app.route('/contabilidad/factura/<int:id>/pagar', methods=['POST'])
@login_required
def factura_pagar(id):
    """
    Marca una factura como pagada. Endpoint de API que responde con JSON.

    Diseñado para ser consumido con fetch() desde el frontend, permitiendo
    actualizar el estado sin recargar la página completa.

    Args:
        id (int): ID de la factura a marcar como pagada.

    Returns:
        JSON con estructura:
        {
            "success"     : bool,
            "message"     : str,
            "nuevo_estado": "Pagada"   (solo si success=True)
        }
        Código HTTP 404 si la factura no existe.
    """
    conn = get_db()

    factura = conn.execute(
        'SELECT numero, estado FROM facturas WHERE id = ?', (id,)
    ).fetchone()

    if not factura:
        conn.close()
        return jsonify({'success': False, 'message': 'Factura no encontrada.'}), 404

    if factura['estado'] == 'Pagada':
        conn.close()
        return jsonify({'success': False,
                        'message': f'La factura {factura["numero"]} ya está marcada como pagada.'})

    # Actualizar estado en la base de datos
    conn.execute("UPDATE facturas SET estado = 'Pagada' WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return jsonify({
        'success':      True,
        'message':      f'Factura {factura["numero"]} marcada como pagada correctamente.',
        'nuevo_estado': 'Pagada'
    })


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULO: REPORTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/reportes')
@login_required
def reportes():
    """
    Página de reportes ejecutivos con 4 gráficos Chart.js y resumen anual.

    Gráfico 1 — Ventas por Mes (Bar Chart):
        Suma de facturas (cualquier estado) para cada uno de los 12 meses
        del año en curso.

    Gráfico 2 — Clientes por Ciudad (Horizontal Bar):
        Top 6 ciudades con más clientes registrados.

    Gráfico 3 — Estado de Facturas (Pie Chart):
        Distribución de facturas por estado: Pagada / Pendiente / Vencida.

    Gráfico 4 — Productos por Categoría (Doughnut):
        Cantidad de productos activos agrupados por categoría.

    Resumen ejecutivo anual:
        mejor_mes, peor_mes, promedio_mensual, total_anual

    Los datos se pasan al template como cadenas JSON para que Chart.js los
    pueda consumir directamente en etiquetas <script>.

    Returns:
        Renderiza templates/reportes.html con todos los datos serializados.
    """
    conn = get_db()
    año_actual    = date.today().year
    nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                     'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    # ── Gráfico 1: Ventas por mes (12 meses del año actual) ────────────────
    ventas_anuales = []
    for mes in range(1, 13):
        prefijo = f'{año_actual}-{mes:02d}'
        total = conn.execute(
            "SELECT COALESCE(SUM(total), 0) AS t FROM facturas WHERE fecha_emision LIKE ?",
            (f'{prefijo}%',)
        ).fetchone()['t']
        ventas_anuales.append(round(total, 2))

    # ── Gráfico 2: Clientes por ciudad (top 6) ─────────────────────────────
    clientes_ciudad = conn.execute(
        """SELECT ciudad, COUNT(*) AS total
           FROM clientes
           GROUP BY ciudad
           ORDER BY total DESC
           LIMIT 6"""
    ).fetchall()
    ciudades_labels  = [r['ciudad'] for r in clientes_ciudad]
    ciudades_valores = [r['total']  for r in clientes_ciudad]

    # ── Gráfico 3: Estado de facturas (Pagada / Pendiente / Vencida) ───────
    estados_rows = conn.execute(
        "SELECT estado, COUNT(*) AS total FROM facturas GROUP BY estado"
    ).fetchall()
    estados_labels  = [r['estado'] for r in estados_rows]
    estados_valores = [r['total']  for r in estados_rows]

    # ── Gráfico 4: Productos activos por categoría ─────────────────────────
    cat_rows = conn.execute(
        """SELECT categoria, COUNT(*) AS total
           FROM productos
           WHERE estado = 'Activo'
           GROUP BY categoria
           ORDER BY total DESC"""
    ).fetchall()
    cat_labels  = [r['categoria'] for r in cat_rows]
    cat_valores = [r['total']     for r in cat_rows]

    conn.close()

    # ── Resumen ejecutivo ──────────────────────────────────────────────────
    total_anual      = sum(ventas_anuales)
    promedio_mensual = total_anual / 12
    mejor_mes_idx    = ventas_anuales.index(max(ventas_anuales))
    peor_mes_idx     = ventas_anuales.index(min(ventas_anuales))

    return render_template('reportes.html',
                           # Gráfico 1
                           meses_labels    = json.dumps(nombres_meses),
                           ventas_anuales  = json.dumps(ventas_anuales),
                           # Gráfico 2
                           ciudades_labels  = json.dumps(ciudades_labels),
                           ciudades_valores = json.dumps(ciudades_valores),
                           # Gráfico 3
                           estados_labels  = json.dumps(estados_labels),
                           estados_valores = json.dumps(estados_valores),
                           # Gráfico 4
                           cat_labels  = json.dumps(cat_labels),
                           cat_valores = json.dumps(cat_valores),
                           # Resumen ejecutivo
                           mejor_mes        = nombres_meses[mejor_mes_idx],
                           peor_mes         = nombres_meses[peor_mes_idx],
                           promedio_mensual = promedio_mensual,
                           total_anual      = total_anual)


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULO: CONFIGURACIÓN DEL SISTEMA
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/configuracion')
@login_required
def configuracion():
    """
    Muestra la página de configuración del sistema con:
    - Información general: versión, ruta de BD, conteo de registros.
    - Tabla de usuarios del sistema (sin mostrar contraseñas).
    - Integrantes del grupo académico.
    - Botón para reiniciar la base de datos.

    Returns:
        Renderiza templates/configuracion.html con los datos del sistema.
    """
    conn = get_db()

    # Contar registros de cada tabla para el panel de información
    num_clientes  = conn.execute("SELECT COUNT(*) AS t FROM clientes").fetchone()['t']
    num_productos = conn.execute("SELECT COUNT(*) AS t FROM productos").fetchone()['t']
    num_facturas  = conn.execute("SELECT COUNT(*) AS t FROM facturas").fetchone()['t']
    num_gastos    = conn.execute("SELECT COUNT(*) AS t FROM gastos").fetchone()['t']
    conn.close()

    # Construir lista de usuarios sin exponer las contraseñas
    usuarios = [
        {'username': usuario, 'nombre': datos['nombre'], 'rol': datos['rol']}
        for usuario, datos in USERS.items()
    ]

    return render_template('configuracion.html',
                           usuarios=usuarios,
                           num_clientes=num_clientes,
                           num_productos=num_productos,
                           num_facturas=num_facturas,
                           num_gastos=num_gastos,
                           db_path=DB_PATH)


@app.route('/configuracion/reiniciar-bd', methods=['POST'])
@login_required
def reiniciar_bd():
    """
    Elimina el archivo de base de datos y lo regenera con los datos seed
    llamando a init_db(). Útil para la defensa académica.

    Returns:
        Redirige a /configuracion con mensaje de resultado.
    """
    try:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)   # Borrar el archivo SQLite existente
        init_db(DB_PATH)         # Recrear tablas e insertar datos seed
        flash('Base de datos reiniciada correctamente con datos de ejemplo.', 'success')
    except Exception as e:
        flash(f'Error al reiniciar la base de datos: {str(e)}', 'danger')
    return redirect(url_for('configuracion'))


# ─────────────────────────────────────────────────────────────────────────────
# MANEJADORES DE ERROR PERSONALIZADOS
# ─────────────────────────────────────────────────────────────────────────────

@app.errorhandler(404)
def pagina_no_encontrada(e):
    """
    Manejador para error 404 (recurso no encontrado).

    Returns:
        Renderiza templates/404.html con código HTTP 404.
    """
    return render_template('404.html'), 404


@app.errorhandler(500)
def error_interno(e):
    """
    Manejador para errores 500 (fallo interno del servidor).

    En modo debug Flask ya muestra el traceback; este handler
    solo aplica cuando debug=False (producción).

    Returns:
        Redirige al dashboard con mensaje de error.
    """
    flash('Error interno del servidor. Por favor intenta de nuevo.', 'danger')
    return redirect(url_for('dashboard'))


# ─────────────────────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    # Inicializar la BD con datos seed si el archivo no existe aún
    if not os.path.exists(DB_PATH):
        init_db(DB_PATH)
        print("Base de datos creada con datos de ejemplo.")
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
