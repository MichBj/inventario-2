from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
import os
import json
import csv
from Conexion.conexion import get_db_connection

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATOS_DIR = os.path.join(BASE_DIR, 'datos')

# ---
# CONFIGURACIÓN DE LA BASE DE DATOS Y RUTA
# ---

def init_db():
    connection = get_db_connection()
    if connection and connection.is_connected():
        cursor = connection.cursor()
        try:
            cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                             (id INT AUTO_INCREMENT PRIMARY KEY, 
                              nombre VARCHAR(255) NOT NULL, 
                              email VARCHAR(255) NOT NULL UNIQUE, 
                              fecha VARCHAR(255))''')
            connection.commit()
            print("Tabla 'usuarios' creada o ya existente.")
        except Error as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            cursor.close()
            connection.close()
    else:
        print("No se pudo establecer conexión con la base de datos.")

# Inicializar la base de datos al iniciar la aplicación
with app.app_context():
    init_db()

# Asegurar que la carpeta 'datos' existe
os.makedirs(DATOS_DIR, exist_ok=True)

# ---
# RUTAS DE LA APLICACIÓN
# ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        fecha = request.form['fecha']

        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            try:
                # Insertar en la base de datos
                cursor.execute("INSERT INTO usuarios (nombre, email, fecha) VALUES (%s, %s, %s)", 
                               (nombre, email, fecha))
                connection.commit()

                # Guardar en archivos
                try:
                    # Guardar en archivo de texto
                    with open(os.path.join(DATOS_DIR, 'datos.txt'), 'a') as f:
                        f.write(f"{nombre},{email},{fecha}\n")

                    # Guardar en archivo JSON (formato de array)
                    json_path = os.path.join(DATOS_DIR, 'datos.json')
                    data = {"nombre": nombre, "email": email, "fecha": fecha}
                    json_data = []

                    if os.path.exists(json_path) and os.path.getsize(json_path) > 0:
                        with open(json_path, 'r') as f:
                            json_data = json.load(f)
                    
                    json_data.append(data)

                    with open(json_path, 'w') as f:
                        json.dump(json_data, f, indent=4)
                    
                    # Guardar en archivo CSV
                    csv_path = os.path.join(DATOS_DIR, 'datos.csv')
                    with open(csv_path, 'a', newline='') as f:
                        writer = csv.writer(f)
                        if os.path.getsize(csv_path) == 0:
                            writer.writerow(['nombre', 'email', 'fecha'])  # Escribir encabezado
                        writer.writerow([nombre, email, fecha])
                
                except Exception as e:
                    print(f"Error al escribir en los archivos: {e}")

            except mysql.connector.IntegrityError:
                return "Error: El email ya está registrado. <a href='/formulario'>Volver</a>"
            except Error as e:
                print(f"Error de base de datos: {e}")
                return "Error al guardar los datos."
            finally:
                cursor.close()
                connection.close()

        return redirect(url_for('resultado', nombre=nombre))
    
    return render_template('formulario.html')

@app.route('/resultado')
def resultado():
    nombre = request.args.get('nombre')
    connection = get_db_connection()
    usuarios = []
    if connection and connection.is_connected():
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT nombre, email, fecha FROM usuarios")
            usuarios = cursor.fetchall()
        except Error as e:
            print(f"Error al obtener datos de la base de datos: {e}")
        finally:
            cursor.close()
            connection.close()
    
    return render_template('resultado.html', nombre=nombre, usuarios=usuarios)

if __name__ == '__main__':
    app.run(debug=True)