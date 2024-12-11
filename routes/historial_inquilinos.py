from flask import Blueprint, render_template, request, jsonify
from conexion import conectar  # Conexión a la base de datos
from utilidades import login_required

bp = Blueprint('historial_inquilinos', __name__)

@bp.route('/historial_inquilinos')
@login_required
def historial_inquilinos():
    try:
        # Conectar a la base de datos
        conn = conectar()
        cursor = conn.cursor()

        # Obtener todos los inquilinos desde la base de datos
        query = "SELECT id, name, idValue, tower, startDate, endDate FROM inquilinos"
        cursor.execute(query)
        inquilinos = cursor.fetchall()  # Obtener todos los resultados

        # Cerrar la conexión
        cursor.close()
        conn.close()

        # Pasar los datos a la plantilla
        return render_template('historial_inquilinos.html', inquilinos=inquilinos)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Ruta para agregar un nuevo inquilino
@bp.route('/addTenant', methods=['POST'])
@login_required
def add_tenant():
    try:
        data = request.get_json()
        name = data['name']
        idValue = data['idValue']
        tower = data['tower']
        startDate = data['startDate']  # Recibir la fecha como texto en formato mes/día/año
        
        # Insertar los datos en la base de datos (sin cambiar el formato de la fecha)
        conn = conectar()
        cursor = conn.cursor()
        query = """
        INSERT INTO inquilinos (name, idValue, tower, startDate)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (name, idValue, tower, startDate))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



@bp.route('/updateEndDate', methods=['POST'])
@login_required
def update_end_date():
    try:
        data = request.get_json()  # Obtener los datos enviados en formato JSON

        tenant_id = data.get('tenant_id')  # ID del inquilino
        end_date = data.get('end_date')  # Fecha de salida

        if not tenant_id or not end_date:
            return jsonify({'success': False, 'error': 'Faltan datos'}), 400

        # Conectar a la base de datos y realizar la actualización
        conn = conectar()
        cursor = conn.cursor()
        query = """
        UPDATE inquilinos
        SET endDate = %s
        WHERE id = %s
        """
        cursor.execute(query, (end_date, tenant_id))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/getHistorial', methods=['POST'])
@login_required
def get_historial():
    try:
        data = request.get_json()
        tower = data.get('tower', '').strip()

        if not tower:
            return jsonify({'success': False, 'error': 'Falta la torre'}), 400

        conn = conectar()
        cursor = conn.cursor()
        query = """
        SELECT id, name, tower, startDate, endDate
        FROM inquilinos
        WHERE tower = %s
        """
        cursor.execute(query, (tower,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        historial = [{'id': r[0], 'nombre': r[1], 'torre': r[2], 'fechaEntrada': r[3], 'fechaSalida': r[4]} for r in rows]
        return jsonify({'success': True, 'historial': historial})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/updateTenant', methods=['POST'])
@login_required
def update_tenant():
    try:
        data = request.get_json()
        tenant_id = data['tenantId']
        updated_data = data['updatedData']
        
        # Actualizar en la base de datos
        conn = conectar()
        cursor = conn.cursor()
        query = """
        UPDATE inquilinos
        SET name = %s, idValue = %s, tower = %s, startDate = %s
        WHERE id = %s
        """
        cursor.execute(query, (
            updated_data['name'],
            updated_data['idValue'],
            updated_data['tower'],
            updated_data['startDate'],
            tenant_id
        ))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
