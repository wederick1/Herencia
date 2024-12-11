from flask import Blueprint, render_template, redirect, jsonify, request
from conexion import conectar  # Función para conectar a la base de datos
from utilidades import login_required

bp = Blueprint('home', __name__)

@bp.route('/')
def inicio():
    return redirect('/home')

@bp.route('/home')
@login_required
def home():
    return render_template("home.html")

# Ruta para obtener los propietarios desde la base de datos
@bp.route('/get_towers_and_owners', methods=['GET'])
def get_towers_and_owners():
    conn = conectar()  # Conectar a la base de datos
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, torre, nombre FROM propietarios")  # Consultamos las torres y los propietarios
        rows = cursor.fetchall()  # Obtenemos los resultados
        result = {row[1]: row[2] for row in rows}  # Creamos el diccionario {torre: nombre}
        conn.close()
        return jsonify(result)  # Retornamos el diccionario como JSON
    else:
        return jsonify({"error": "No se pudo conectar a la base de datos."}), 500

@bp.route('/add_visitor', methods=['POST'])
def add_visitor():
    # Obtenemos los datos del formulario enviados desde el frontend
    name = request.form['name']
    id_value = request.form['idValue']
    role = request.form['role']
    tower = request.form['tower']
    owner_type = request.form['ownerType']  # Dueño/Inquilino
    date = request.form['date']  # Fecha de entrada
    entry_time = request.form['entryTime']  # Hora de entrada

    # Conectamos a la base de datos
    conn = conectar()
    if conn:
        cursor = conn.cursor()

        # Verificamos que el propietario exista según la torre y el nombre
        cursor.execute("SELECT id FROM propietarios WHERE torre = %s AND nombre = %s", (tower, owner_type))
        propietario_id = cursor.fetchone()

        if propietario_id:
            propietario_id = propietario_id[0]

            # Insertamos el historial en la tabla 'historial'
            cursor.execute("""
                INSERT INTO historial (fecha, nombre, identificacion, rol, torre, propietario_id, hora_entrada)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (date, name, id_value, role, tower, propietario_id, entry_time))

            # Obtenemos el ID del historial insertado
            historial_id = cursor.fetchone()[0]

            # Confirmamos los cambios y cerramos la conexión
            conn.commit()
            conn.close()

            return jsonify({"message": "Visitante agregado y historial registrado correctamente.", "historial_id": historial_id}), 201
        else:
            conn.close()
            return jsonify({"error": "No se encontró el propietario correspondiente."}), 404
    else:
        return jsonify({"error": "No se pudo conectar a la base de datos."}), 500
    

    
@bp.route('/mark_exit', methods=['POST'])
def mark_exit():
    try:
        # Obtener datos del formulario con un valor por defecto en caso de ausencia
        visitor_id = request.form.get('visitor_id')
        exit_time = request.form.get('exit_time')
        print(exit_time)
        print(visitor_id)

        # Validar que ambos datos estén presentes
        if not visitor_id or not exit_time:
            return jsonify({"error": "Datos incompletos: visitor_id o exit_time faltan."}), 400

        # Intentar conectar a la base de datos
        conn = conectar()
        if not conn:
            return jsonify({"error": "No se pudo conectar a la base de datos."}), 500

        cursor = conn.cursor()

        # Actualizar la hora de salida
        cursor.execute("""
            UPDATE historial
            SET hora_salida = %s
            WHERE id = %s
        """, (exit_time, visitor_id))

        # Confirmar cambios
        conn.commit()
        conn.close()

        # Respuesta exitosa
        return jsonify({"message": "Hora de salida registrada correctamente."}), 200

    except KeyError as e:
        # Manejar errores específicos de claves faltantes
        return jsonify({"error": f"Clave faltante en la solicitud: {str(e)}"}), 400
    except Exception as e:
        # Manejar cualquier otro error
        print("Error en mark_exit:", e)
        return jsonify({"error": "Error interno del servidor."}), 500


@bp.route('/get_next_id', methods=['GET'])
def get_next_id():
    try:
        conn = conectar()
        if not conn:
            return jsonify({"error": "No se pudo conectar a la base de datos."}), 500

        cursor = conn.cursor()

        # Consulta para obtener el siguiente ID
        cursor.execute("SELECT MAX(id) + 1 AS next_id FROM historial")
        result = cursor.fetchone()
        next_id = result[0] if result[0] is not None else 1  # Si no hay filas, el próximo ID será 1

        conn.close()

        return jsonify({"next_id": next_id}), 200

    except Exception as e:
        print("Error en get_next_id:", e)
        return jsonify({"error": "Error interno del servidor."}), 500


@bp.route('/add_visit', methods=['POST'])
def add_visit():
    # Obtenemos los datos del formulario enviados desde el frontend
    name = request.form['name']
    id_value = request.form['idValue']  # Cédula del visitante
    role = request.form['role']
    tower = request.form['tower']
    owner_type = request.form['ownerType']  # Nombre del propietario

    # Normalizamos los datos
    tower_normalized = tower.strip().upper()
    owner_type_normalized = owner_type.strip().upper()

    # Conectamos a la base de datos
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()

            # Verificamos que el propietario exista según la torre y el nombre
            query = """
                SELECT id FROM propietarios 
                WHERE UPPER(TRIM(torre)) = %s AND UPPER(TRIM(nombre)) = %s
            """
            cursor.execute(query, (tower_normalized, owner_type_normalized))
            propietario_id = cursor.fetchone()

            if propietario_id:
                propietario_id = propietario_id[0]

                # Verificar si el visitante ya existe (basado en la cédula)
                cursor.execute("SELECT id, nombre FROM visitantes WHERE cedula = %s", (id_value,))
                existing_visitor = cursor.fetchone()

                if existing_visitor:
                    # Si el visitante ya existe, damos la bienvenida
                    conn.close()
                    return jsonify({
                        "message": f"Bienvenido nuevamente, {existing_visitor[1]}!",
                        "visitor_id": existing_visitor[0]
                    }), 200

                # Insertamos el visitante en la tabla 'visitantes' si no existe
                cursor.execute("""
                    INSERT INTO visitantes (nombre, cedula, rol, torre, propietario_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (name, id_value, role, tower_normalized, propietario_id))

                # Obtenemos el ID del visitante insertado
                visitante_id = cursor.fetchone()[0]

                # Confirmamos los cambios y cerramos la conexión
                conn.commit()
                conn.close()

                return jsonify({
                    "message": "Visitante agregado correctamente.",
                    "visitante_id": visitante_id
                }), 201
            else:
                # Si no se encontró el propietario
                print(f"Propietario no encontrado: Torre={tower_normalized}, Nombre={owner_type_normalized}")
                conn.close()
                return jsonify({"error": "No se encontró el propietario correspondiente."}), 404
        except Exception as e:
            # Manejo de errores inesperados
            conn.rollback()
            print(f"Error al procesar la solicitud: {e}")
            conn.close()
            return jsonify({"error": "Ocurrió un error al procesar la solicitud."}), 500
    else:
        return jsonify({"error": "No se pudo conectar a la base de datos."}), 500


# Ruta para obtener los datos de los visitantes
@bp.route('/get_visitor_data', methods=['GET'])
def get_visitor_data():
    # Usar la función conectar para obtener la conexión
    conn = conectar()
    cursor = conn.cursor()

    # Ejecutar una consulta SQL para obtener los visitantes
    cursor.execute("SELECT nombre, cedula, rol, torre, propietario_id FROM visitantes")
    visitantes = cursor.fetchall()

    # Convertir los resultados en un formato adecuado para el frontend
    visitor_list = []
    for visitante in visitantes:
        visitor_list.append({
            'nombre': visitante[0],
            'cedula': visitante[1],
            'rol': visitante[2],
            'torre': visitante[3],
            'propietario_id': visitante[4]

        })

    cursor.close()  # Cerrar el cursor
    conn.close()  # Cerrar la conexión

    # Devolver los datos al frontend en formato JSON
    return jsonify(visitor_list)




