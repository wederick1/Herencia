from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from conexion import conectar  # Conexión a la base de datos
from utilidades import login_required

bp = Blueprint('historial', __name__)

@bp.route('/historial')
@login_required
def historial():
    return render_template('historial.html')

@bp.route('/api/historial')
def obtener_historial():
    conn = conectar()
    cursor = conn.cursor()
    # Consulta SQL con JOIN para obtener el nombre del propietario
    query = """
    SELECT 
        h.id, 
        h.fecha, 
        h.nombre, 
        h.identificacion, 
        h.rol, 
        h.torre, 
        p.nombre AS propietario, 
        h.hora_entrada, 
        h.hora_salida
    FROM historial h
    LEFT JOIN propietarios p ON h.propietario_id = p.id
    """
    cursor.execute(query)
    columnas = [desc[0] for desc in cursor.description]
    datos = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    conn.close()
    return jsonify(datos)


