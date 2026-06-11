# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PokéShop TCG — Admin, Categorías y Dashboard
#  Tecnologías: Flask, SQLite, HTML, CSS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'pokeshop123'

# ── Credenciales del administrador ──────────────
# Para cambiarlas, edita estas dos líneas:
ADMIN_USUARIO  = 'admin'
ADMIN_PASSWORD = 'admin123'

# Categorías disponibles para las cartas
CATEGORIAS = ['Fuego', 'Agua', 'Eléctrico', 'Planta', 'Psíquico', 'Dragón', 'Normal']

# --- Conectar a la base de datos ---
def get_db():
    conn = sqlite3.connect('tienda.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- Crear tablas si no existen ---
def init_db():
    with get_db() as db:
        db.executescript('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario  TEXT UNIQUE NOT NULL,
                email    TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS cartas (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre    TEXT NOT NULL,
                precio    INTEGER NOT NULL,
                imagen    TEXT NOT NULL,
                categoria TEXT NOT NULL DEFAULT 'Normal'
            );
        ''')

def encriptar(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- Cargar cartas de ejemplo (solo si la tabla está vacía) ---
def cargar_ejemplos():
    with get_db() as db:
        total = db.execute('SELECT COUNT(*) FROM cartas').fetchone()[0]
        if total == 0:
            ejemplos = [
                ('Pikachu ex',    45,  'https://images.pokemontcg.io/sv3pt5/28_hires.png', 'Eléctrico'),
                ('Charizard ex',  120, 'https://images.pokemontcg.io/sv1/6_hires.png',     'Fuego'),
                ('Mewtwo ex',     80,  'https://images.pokemontcg.io/sv2/52_hires.png',    'Psíquico'),
                ('Gardevoir ex',  60,  'https://images.pokemontcg.io/sv3/91_hires.png',    'Psíquico'),
                ('Lucario ex',    35,  'https://images.pokemontcg.io/sv4/55_hires.png',    'Normal'),
                ('Eevee ex',      50,  'https://images.pokemontcg.io/sv5/25_hires.png',    'Normal'),
                ('Blastoise ex',  95,  'https://images.pokemontcg.io/sv3pt5/9_hires.png',  'Agua'),
                ('Rayquaza ex',   110, 'https://images.pokemontcg.io/sv6/110_hires.png',   'Dragón'),
                ('Venusaur ex',   85,  'https://images.pokemontcg.io/sv3pt5/3_hires.png',  'Planta'),
            ]
            for nombre, precio, imagen, categoria in ejemplos:
                db.execute(
                    'INSERT INTO cartas (nombre, precio, imagen, categoria) VALUES (?, ?, ?, ?)',
                    (nombre, precio, imagen, categoria)
                )

# ══════════════════════════════════════════════
#  RUTAS PÚBLICAS
# ══════════════════════════════════════════════

@app.route('/')
def inicio():
    return render_template('inicio.html', usuario=session.get('usuario'))

# CATÁLOGO — lee de la base de datos, con filtro opcional por categoría
@app.route('/catalogo')
def catalogo():
    categoria = request.args.get('categoria')  # ?categoria=Fuego en la URL

    with get_db() as db:
        if categoria and categoria != 'Todos':
            cartas = db.execute('SELECT * FROM cartas WHERE categoria=?', (categoria,)).fetchall()
        else:
            cartas = db.execute('SELECT * FROM cartas').fetchall()

    return render_template(
        'catalogo.html',
        cartas=cartas,
        categorias=CATEGORIAS,
        categoria_activa=categoria or 'Todos',
        usuario=session.get('usuario')
    )

# SERVICIOS — página de gradeado
@app.route('/servicios')
def servicios():
    return render_template('servicios.html', usuario=session.get('usuario'))

# ══════════════════════════════════════════════
#  REGISTRO Y LOGIN
# ══════════════════════════════════════════════

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario  = request.form['usuario']
        email    = request.form['email']
        password = request.form['password']
        try:
            with get_db() as db:
                db.execute(
                    'INSERT INTO usuarios (usuario, email, password) VALUES (?, ?, ?)',
                    (usuario, email, encriptar(password))
                )
            flash('¡Cuenta creada! Ahora puedes iniciar sesión.', 'ok')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Ese usuario o correo ya existe.', 'error')
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario  = request.form['usuario']
        password = request.form['password']
        with get_db() as db:
            user = db.execute(
                'SELECT * FROM usuarios WHERE usuario=? AND password=?',
                (usuario, encriptar(password))
            ).fetchone()
        if user:
            session['usuario'] = user['usuario']
            flash(f'Bienvenido, {user["usuario"]}!', 'ok')
            return redirect(url_for('catalogo'))
        else:
            flash('Usuario o contraseña incorrectos.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('inicio'))

# ══════════════════════════════════════════════
#  CARRITO
# ══════════════════════════════════════════════

@app.route('/carrito')
def carrito():
    mi_carrito = session.get('carrito', [])
    total = sum(item['precio'] * item['cantidad'] for item in mi_carrito)
    return render_template('carrito.html', carrito=mi_carrito, total=total, usuario=session.get('usuario'))

@app.route('/agregar/<nombre>/<int:precio>')
def agregar(nombre, precio):
    carrito = session.get('carrito', [])
    for item in carrito:
        if item['nombre'] == nombre:
            item['cantidad'] += 1
            session['carrito'] = carrito
            flash(f'{nombre} actualizado en el carrito.', 'ok')
            return redirect(url_for('catalogo'))
    carrito.append({'nombre': nombre, 'precio': precio, 'cantidad': 1})
    session['carrito'] = carrito
    flash(f'{nombre} agregado al carrito!', 'ok')
    return redirect(url_for('catalogo'))

@app.route('/vaciar')
def vaciar():
    session.pop('carrito', None)
    return redirect(url_for('carrito'))

# ══════════════════════════════════════════════
#  PANEL ADMIN
# ══════════════════════════════════════════════

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['usuario'] == ADMIN_USUARIO and \
           request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        flash('Credenciales incorrectas.', 'error')
    return render_template('admin_login.html')

# DASHBOARD — estadísticas generales
@app.route('/admin')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    with get_db() as db:
        cartas    = db.execute('SELECT * FROM cartas').fetchall()
        usuarios  = db.execute('SELECT COUNT(*) FROM usuarios').fetchone()[0]

        # Estadísticas para el dashboard
        total_cartas = len(cartas)
        valor_total  = sum(c['precio'] for c in cartas)

        # Conteo de cartas por categoría (para el gráfico)
        conteo_categorias = db.execute('''
            SELECT categoria, COUNT(*) as cantidad
            FROM cartas
            GROUP BY categoria
        ''').fetchall()

    return render_template(
        'admin_panel.html',
        cartas=cartas,
        categorias=CATEGORIAS,
        total_cartas=total_cartas,
        total_usuarios=usuarios,
        valor_total=valor_total,
        conteo_categorias=conteo_categorias
    )

@app.route('/admin/agregar', methods=['POST'])
def admin_agregar():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    nombre    = request.form['nombre']
    precio    = request.form['precio']
    imagen    = request.form['imagen']
    categoria = request.form['categoria']
    with get_db() as db:
        db.execute(
            'INSERT INTO cartas (nombre, precio, imagen, categoria) VALUES (?, ?, ?, ?)',
            (nombre, precio, imagen, categoria)
        )
    flash(f'Carta "{nombre}" agregada correctamente.', 'ok')
    return redirect(url_for('admin_panel'))

@app.route('/admin/eliminar/<int:id>')
def admin_eliminar(id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    with get_db() as db:
        db.execute('DELETE FROM cartas WHERE id=?', (id,))
    flash('Carta eliminada.', 'ok')
    return redirect(url_for('admin_panel'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('inicio'))

# ══════════════════════════════════════════════
#  INICIAR APP
# ══════════════════════════════════════════════
if __name__ == '__main__':
    init_db()
    cargar_ejemplos()
    app.run(debug=True)
