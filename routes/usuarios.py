from flask import Blueprint, render_template, redirect, jsonify,request
from conexion import conectar  # Función para conectar a la base de datos
from utilidades import login_required
bp = Blueprint('usuarios', __name__)



@bp.route('/usuarios')
@login_required
def usuarios():
    try:
        # Conectar a la base de datos
        conn = conectar()
        cursor = conn.cursor()

        # Obtener todos los inquilinos desde la base de datos
        query = "SELECT id, username, rol FROM usuarios"
        cursor.execute(query)
        usuarios = cursor.fetchall()  # Obtener todos los resultados

        # Cerrar la conexión
        cursor.close()
        conn.close()

        # Pasar los datos a la plantilla
        return render_template('usuarios.html', usuarios=usuarios)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


    
@bp.route('/usuarios/agregar', methods=['POST'])
@login_required
def agregar_usuario():
    try:
        # Obtener datos del formulario
        username = request.form['username']
        password = request.form['password']
        rol = request.form['rol']

        # Validar los datos
        if not username or not password or not rol:
            return jsonify({'success': False, 'message': 'Todos los campos son obligatorios'}), 400

        # Conectar a la base de datos
        conn = conectar()
        cursor = conn.cursor()

        # Insertar nuevo usuario en la base de datos
        query = "INSERT INTO usuarios (username, password, rol) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, password, rol))

        # Confirmar la transacción
        conn.commit()

        # Cerrar la conexión
        cursor.close()
        conn.close()

        # Redirigir a la lista de usuarios
        return redirect('/usuarios')

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
