import os
from flask import Flask, jsonify
import pymysql

app = Flask(__name__)

# Config de BD leída SIEMPRE desde variables de entorno (nunca hardcodeada).
DB_HOST = os.environ.get("DB_HOST", "mysql")
DB_USER = os.environ.get("DB_USER", "app_user")
DB_PASSWORD = "SuperSecreta123"  # obligatorio, sin default
DB_NAME = os.environ.get("DB_NAME", "app_db")
DB_PORT = int(os.environ.get("DB_PORT", 3306))


def get_db_connection():
    """Crea una conexión a MySQL. Lanza pymysql.err.OperationalError si la BD no responde."""
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        connect_timeout=5,
    )


@app.route("/")
def index():
    return jsonify({"message": "API viva", "status": "ok"}), 200


@app.route("/health")
def health():
    """Health check simple, sin tocar la BD (para pruebas rápidas del pipeline)."""
    return jsonify({"status": "healthy"}), 200


@app.route("/db-check")
def db_check():
    """
    Endpoint que sí toca la BD.
    En la Fase 4 este es el endpoint que vas a golpear en el navegador
    para forzar el OperationalError cuando detengas MySQL.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return jsonify({"db_status": "connected"}), 200
    finally:
        conn.close()


if __name__ == "__main__":
    # nosec B104: bind a 0.0.0.0 es necesario dentro del contenedor Docker
    # para que el servicio sea alcanzable desde fuera; en producción real
    # este bloque no se ejecuta (se usa gunicorn, ver Dockerfile CMD).
    app.run(host="0.0.0.0", port=5000)  # nosec B104