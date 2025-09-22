# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from Conexion.conexion import get_db_connection, init_db
from models import User
import bcrypt
import mysql.connector

app = Flask(__name__)
app.secret_key = 'proyecto_desarrollo_web_2025'  # Clave secreta para sesiones

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Inicializar la base de datos
with app.app_context():
    init_db()

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Rutas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            try:
                cursor.execute("INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)", 
                               (nombre, email, hashed_password))
                connection.commit()
                flash('Registro exitoso. Por favor, inicia sesión.', 'success')
                return redirect(url_for('resultado', nombre=nombre))
            except mysql.connector.IntegrityError:
                flash('Error: El email ya está registrado.', 'error')
                return redirect(url_for('formulario'))
            except Exception as e:
                flash(f'Error al registrar: {e}', 'error')
                return redirect(url_for('formulario'))
            finally:
                cursor.close()
                connection.close()
    return render_template('formulario.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        user, stored_password = User.get_by_email(email)
        if user and stored_password and bcrypt.checkpw(password, stored_password.encode('utf-8')):
            login_user(user)
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email o contraseña incorrectos.', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada exitosamente.', 'success')
    return redirect(url_for('index'))

@app.route('/resultado')
def resultado():
    nombre = request.args.get('nombre')
    connection = get_db_connection()
    usuarios = []
    if connection and connection.is_connected():
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id_usuario, nombre, email FROM usuarios")
            usuarios = cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener datos: {e}")
        finally:
            cursor.close()
            connection.close()
    return render_template('resultado.html', nombre=nombre, usuarios=usuarios)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', nombre=current_user.nombre)

if __name__ == '__main__':
    app.run(debug=True)