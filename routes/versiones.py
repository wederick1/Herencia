from flask import Blueprint, render_template, jsonify, send_file
from version_utils import obtener_releases,  descargar_y_extraer_zip 
from utilidades import login_required  # Asegúrate de tener esta función para autenticación
import os, shutil, requests


# Definir UPLOAD_FOLDER dentro de este archivo
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "archivos")     # Carpeta para guardar archivos

# Crear la carpeta si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

bp = Blueprint('versiones', __name__)

# Ruta para mostrar las versiones
@bp.route('/versiones')
@login_required
def versiones():
    # Obtener las versiones desde la función obtener_releases
    versions, new_version_available, _ = obtener_releases()

    # Enviar las versiones y el estado de la nueva versión al template
    return render_template("versiones.html", versions=versions, new_version_available=new_version_available)

# Ruta para comprobar si hay una nueva versión
@bp.route('/check_for_update', methods=['POST'])
@login_required
def check_for_update():
    # Llamamos a la función que obtiene las versiones desde GitHub
    versions, new_version_available, _ = obtener_releases()

    # Retornar si hay una nueva versión disponible
    return jsonify({"new_version_available": new_version_available})

@bp.route('/download_latest_version', methods=['GET'])
def download_latest_version():
    try:
        # Obtener la última versión y los datos
        versions, new_version_available, latest_release = obtener_releases()

        if latest_release and latest_release["assets"]:
            downloaded_files = []  # Lista para registrar archivos descargados

            # Directorio donde se guardarán los archivos extraídos
            DESTINATION_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

            # Descargar y extraer el archivo ZIP
            for asset in latest_release["assets"]:
                asset_url = asset["browser_download_url"]
                file_name = asset["name"]
                file_path = os.path.join(UPLOAD_FOLDER, file_name)

                # Descargar y extraer el archivo ZIP en la carpeta `archivos/versiones`
                success, message = descargar_y_extraer_zip(asset_url, file_name, UPLOAD_FOLDER)

                if success:
                    downloaded_files.append(file_name)
                else:
                    return jsonify({"error": message}), 400

            # Mover los archivos extraídos de "archivos/versiones" al destino
            versiones_folder = os.path.join(UPLOAD_FOLDER, 'versiones')
            if os.path.exists(versiones_folder):
                        # Recorrer la carpeta 'versiones' y mover los archivos con su estructura de directorios
                        for root, dirs, files in os.walk(versiones_folder):
                            for file in files:
                                # Ruta completa del archivo en 'versiones'
                                source_path = os.path.join(root, file)
                                # Mantenemos la estructura de directorios en el destino
                                relative_path = os.path.relpath(source_path, versiones_folder)
                                destination_path = os.path.join(DESTINATION_FOLDER, relative_path)

                                # Crear el directorio destino si no existe
                                os.makedirs(os.path.dirname(destination_path), exist_ok=True)

                                # Si el archivo ya existe, eliminarlo
                                if os.path.exists(destination_path):
                                    os.remove(destination_path)

                                # Mover el archivo
                                shutil.move(source_path, destination_path)

                        # Eliminar la carpeta 'versiones' si está vacía
                        if not os.listdir(versiones_folder):
                            os.rmdir(versiones_folder)

            return jsonify({"message": "Archivos descargados y extraídos correctamente", "files": downloaded_files}), 200

        return jsonify({"error": "No hay archivos disponibles para descargar en la última versión."}), 400

    except requests.RequestException as e:
        print(f"Error al descargar los archivos: {e}")
        return jsonify({"error": f"Error al descargar los archivos: {str(e)}"}), 500

    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500
