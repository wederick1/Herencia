from flask import Blueprint, render_template, jsonify, send_file
from version_utils import obtener_releases,  descargar_y_extraer_zip, leer_detalles_version
from utilidades import login_required  # Asegúrate de tener esta función para autenticación
import os, shutil, requests
from datetime import datetime


# Definir UPLOAD_FOLDER dentro de este archivo
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "archivos")     # Carpeta para guardar archivos

# Crear la carpeta si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

bp = Blueprint('versiones', __name__)

@bp.route('/versiones')
@login_required
def versiones():
    try:
        # Leer los detalles de la versión actual desde el archivo
        detalles = leer_detalles_version()

        # Obtener la información de releases desde GitHub
        _, new_version_available, latest_release = obtener_releases()

        # Crear un diccionario para la versión más reciente
        if latest_release:
            detalles_nueva_version = {
                "nombre": latest_release["name"],
                "fecha": datetime.strptime(latest_release["created_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y"),
                "descripcion": latest_release.get("body", "Sin descripción"),
                "url": latest_release["html_url"],
            }
        else:
            detalles_nueva_version = None

        return render_template(
            "versiones.html",
            detalles=[detalles],  # Versión instalada
            new_version_available=new_version_available,  # Si hay nueva versión
            detalles_nueva_version=detalles_nueva_version  # Detalles de la nueva versión, si existe
        )

    except Exception as e:
        return render_template("versiones.html")



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
                if os.listdir(versiones_folder):
                    shutil.rmtree(versiones_folder)
                    shutil.rmtree(UPLOAD_FOLDER)


                # Crear el archivo Version_details.txt con los detalles de la versión
            version_details_path = os.path.join(DESTINATION_FOLDER, "Version_details.txt")
            with open(version_details_path, 'w', encoding='utf-8') as f:
                f.write(f"Nombre de la versión: {latest_release['name']}\n")
                f.write(f"Descripción: {latest_release.get('body', 'No disponible')}\n")
                f.write(f"Fecha de creación: {latest_release['created_at']}\n")


            return jsonify({"message": "Archivos descargados y extraídos correctamente", "files": downloaded_files}), 200

        return jsonify({"error": "No hay archivos disponibles para descargar en la última versión."}), 400

    except requests.RequestException as e:
        print(f"Error al descargar los archivos: {e}")
        return jsonify({"error": f"Error al descargar los archivos: {str(e)}"}), 500

    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500