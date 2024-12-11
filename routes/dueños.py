from flask import Blueprint, render_template, request, jsonify
import pandas as pd
from io import BytesIO
from conexion import conectar  # Supongamos que conecta a tu base de datos.

bp = Blueprint('dueños', __name__)

@bp.route('/agregar-propietario')
def agregar_propietario():
    return render_template("propietarios.html")

@bp.route('/api/propietarios', methods=['GET', 'POST'])
def manejar_propietarios():
    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT id, nombre, torre FROM propietarios")
        propietarios = cursor.fetchall()
        conn.close()
        return jsonify(propietarios)

    elif request.method == 'POST':
        data = request.form
        nombre = data.get('nombre')
        torre = data.get('torre')

        if nombre and torre:
            # Normalización de los datos: eliminación de espacios y convertir a mayúsculas
            nombre_normalizado = nombre.strip().upper()
            torre_normalizada = torre.strip().upper()

            try:
                # Insertar el propietario en la base de datos
                cursor.execute(
                    "INSERT INTO propietarios (nombre, torre) VALUES (%s, %s)",
                    (nombre_normalizado, torre_normalizada)
                )
                conn.commit()
                conn.close()
                return jsonify({'message': 'Propietario agregado exitosamente.'}), 201
            except Exception as e:
                conn.rollback()  # Deshacer cambios si ocurre un error
                conn.close()
                return jsonify({'error': f'Error al insertar propietario: {str(e)}'}), 500
        else:
            conn.close()
            return jsonify({'error': 'Nombre y torre son requeridos.'}), 400


@bp.route('/api/propietarios/excel', methods=['POST'])
def agregar_propietarios_excel():
    conn = conectar()
    cursor = conn.cursor()

    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo.'}), 400

    file = request.files['file']
    try:
        # Leer el archivo Excel
        excel_data = pd.read_excel(BytesIO(file.read()))
        for _, row in excel_data.iterrows():
            nombre = row.get('nombre')
            torre = row.get('torre')
            if pd.notna(nombre) and pd.notna(torre):
                # Normalización de los datos: eliminación de espacios y convertir a mayúsculas
                nombre_normalizado = str(nombre).strip().upper()
                torre_normalizada = str(torre).strip().upper()

                try:
                    # Insertar cada propietario en la base de datos
                    cursor.execute(
                        "INSERT INTO propietarios (nombre, torre) VALUES (%s, %s)",
                        (nombre_normalizado, torre_normalizada)
                    )
                except Exception as e:
                    # Si ocurre un error al insertar, se registra y continúa con el siguiente
                    print(f"Error al insertar propietario {nombre_normalizado} en torre {torre_normalizada}: {str(e)}")
                    continue
        conn.commit()
        conn.close()
        return jsonify({'message': 'Propietarios agregados desde Excel.'}), 201

    except Exception as e:
        conn.close()
        return jsonify({'error': f'Error al procesar el archivo Excel: {str(e)}'}), 500
