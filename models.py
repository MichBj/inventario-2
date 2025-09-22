# models.py
from flask_login import UserMixin
from Conexion.conexion import get_db_connection

class User(UserMixin):
    def __init__(self, id_usuario, nombre, email):
        self.id = id_usuario
        self.nombre = nombre
        self.email = email

    @staticmethod
    def get(user_id):
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT id_usuario, nombre, email FROM usuarios WHERE id_usuario = %s", (user_id,))
                user_data = cursor.fetchone()
                if user_data:
                    return User(user_data[0], user_data[1], user_data[2])
                return None
            except Exception as e:
                print(f"Error al cargar usuario: {e}")
                return None
            finally:
                cursor.close()
                connection.close()
        return None

    @staticmethod
    def get_by_email(email):
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT id_usuario, nombre, email, password FROM usuarios WHERE email = %s", (email,))
                user_data = cursor.fetchone()
                if user_data:
                    return User(user_data[0], user_data[1], user_data[2]), user_data[3]  # Retorna usuario y contraseña
                return None, None
            except Exception as e:
                print(f"Error al cargar usuario por email: {e}")
                return None, None
            finally:
                cursor.close()
                connection.close()
        return None, None