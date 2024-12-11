from flask import Blueprint, render_template, redirect, jsonify, request
from conexion import conectar  # Función para conectar a la base de datos
from utilidades import login_required

bp = Blueprint('versiones', __name__)

versions = [
    {"version": "1.0.0", "date": "2023-01-15", "description": "Lanzamiento inicial"},
    {"version": "1.1.0", "date": "2023-03-10", "description": "Mejoras en la interfaz"},
    {"version": "1.2.0", "date": "2023-06-05", "description": "Corrección de errores y optimización"},
    {"version": "2.0.0", "date": "2024-12-01", "description": "Nuevo diseño y funciones avanzadas"}
]

@bp.route('/versiones')
@login_required
def versiones():
    return render_template("versiones.html", versions=versions)