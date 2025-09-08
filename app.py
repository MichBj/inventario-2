from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret-key'

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Usuario {self.nombre}>'

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}

with app.app_context():
    if not os.path.exists('database'):
        os.makedirs('database')
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html', title='Inicio')

@app.route('/formulario')
def mostrar_formulario():
    return render_template('formulario.html', title='Formulario de Datos')

# ==================== Rutas para Persistencia con Archivos ====================

@app.route('/guardar-txt', methods=['POST'])
def guardar_txt():
    data_to_save = request.form.get('data')
    if not os.path.exists('datos'):
        os.makedirs('datos')
    with open('datos/datos.txt', 'a') as f:
        f.write(data_to_save + '\n')
    flash("Datos guardados en datos.txt", 'success')
    return redirect(url_for('leer_txt'))

@app.route('/leer-txt')
def leer_txt():
    datos = []
    if os.path.exists('datos/datos.txt'):
        with open('datos/datos.txt', 'r') as f:
            datos = [line.strip() for line in f.readlines()]
    return render_template('resultado.html', titulo="Datos de TXT", datos=datos)

@app.route('/guardar-json', methods=['POST'])
def guardar_json():
    new_data = {
        'nombre': request.form.get('nombre'),
        'valor': request.form.get('valor')
    }
    if not os.path.exists('datos'):
        os.makedirs('datos')
    all_data = []
    if os.path.exists('datos/datos.json') and os.path.getsize('datos/datos.json') > 0:
        with open('datos/datos.json', 'r') as f:
            all_data = json.load(f)
    all_data.append(new_data)
    with open('datos/datos.json', 'w') as f:
        json.dump(all_data, f, indent=4)
    flash("Datos guardados en datos.json", 'success')
    return redirect(url_for('leer_json'))

@app.route('/leer-json')
def leer_json():
    datos = []
    if os.path.exists('datos/datos.json') and os.path.getsize('datos/datos.json') > 0:
        with open('datos/datos.json', 'r') as f:
            datos = json.load(f)
    return render_template('resultado.html', titulo="Datos de JSON", datos=datos)

@app.route('/guardar-csv', methods=['POST'])
def guardar_csv():
    headers = ['nombre', 'valor']
    new_row = [request.form.get('nombre'), request.form.get('valor')]
    if not os.path.exists('datos'):
        os.makedirs('datos')
    file_exists = os.path.exists('datos/datos.csv')
    with open('datos/datos.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(new_row)
    flash("Datos guardados en datos.csv", 'success')
    return redirect(url_for('leer_csv'))

@app.route('/leer-csv')
def leer_csv():
    datos = []
    if os.path.exists('datos/datos.csv'):
        with open('datos/datos.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                datos.append(row)
    return render_template('resultado.html', titulo="Datos de CSV", datos=datos)

# ==================== Rutas para Persistencia con SQLite ====================

@app.route('/guardar-bd', methods=['POST'])
def guardar_bd():
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    
    nuevo_usuario = Usuario(nombre=nombre, email=email)
    
    try:
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Usuario guardado en la base de datos.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al guardar usuario: {e}', 'error')
        
    return redirect(url_for('leer_bd'))

@app.route('/leer-bd')
def leer_bd():
    usuarios = Usuario.query.all()
    return render_template('resultado.html', titulo="Datos de la Base de Datos", datos=usuarios)

if __name__ == '__main__':
    app.run(debug=True)