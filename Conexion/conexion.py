# conexion/conexion.py
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """
    Establece y devuelve una conexión a la base de datos MySQL.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root", 
            password="1230", 
            database="inventario_2"
        )
        return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def init_db():
    """
    Crea la tabla 'usuarios' si no existe.
    """
    connection = get_db_connection()
    if connection and connection.is_connected():
        cursor = connection.cursor()
        try:
            cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                            (id_usuario INT AUTO_INCREMENT PRIMARY KEY, 
                             nombre VARCHAR(255) NOT NULL, 
                             email VARCHAR(255) NOT NULL UNIQUE, 
                             password VARCHAR(255) NOT NULL)''')
            connection.commit()
            print("Tabla 'usuarios' creada o ya existente.")
        except Error as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if connection.is_connected():
                connection.close()