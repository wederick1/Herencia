import requests
from datetime import datetime
import zipfile
import os

# URL de la API de GitHub para obtener los releases
GITHUB_RELEASES_URL = "https://api.github.com/repos/wederick1/Herencia/releases"

def obtener_releases():
    try:
        response = requests.get(GITHUB_RELEASES_URL)
        response.raise_for_status()  # Si ocurre un error HTTP

        releases = response.json()  # Parsear la respuesta JSON
        versions = []
        new_version_available = False
        latest_release = None

        for release in releases:
            release_date = datetime.strptime(release["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            formatted_date = release_date.strftime("%d/%m/%Y")

            version_data = {
                "version": release["name"],
                "date": formatted_date,
                "description": release.get("body", "Sin descripción"),
                "url": release["html_url"],
                "assets": release.get("assets", [])
            }

            versions.append(version_data)

            # Comprobar si hay una nueva versión
            if not release["prerelease"]:
                new_version_available = True

            # Determinar el último release
            if not latest_release or release_date > datetime.strptime(latest_release["created_at"], "%Y-%m-%dT%H:%M:%SZ"):
                latest_release = release

        return versions, new_version_available, latest_release

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener los releases de GitHub: {e}")
        return [], False, None

def descargar_y_extraer_zip(asset_url, file_name, output_folder):
    """
    Descarga y extrae un archivo ZIP, y organiza su contenido en una carpeta llamada 'versiones'.
    """
    try:
        response = requests.get(asset_url)
        response.raise_for_status()

        # Ruta completa donde se guardará el archivo ZIP
        zip_path = os.path.join(output_folder, file_name)

        # Guardar el archivo ZIP en el directorio de salida
        with open(zip_path, 'wb') as f:
            f.write(response.content)

        # Ruta para extraer los archivos en una carpeta "versiones"
        versiones_folder = os.path.join(output_folder, 'versiones')
        if not os.path.exists(versiones_folder):
            os.makedirs(versiones_folder)

        # Verificar si es un archivo ZIP válido
        if zipfile.is_zipfile(zip_path):
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extraer todo el contenido en la carpeta "versiones"
                zip_ref.extractall(versiones_folder)

            # Eliminar el archivo ZIP después de la extracción
            os.remove(zip_path)

            return True, f"Archivo ZIP descargado y extraído correctamente en {versiones_folder}."
        else:
            # Si no es un ZIP válido, eliminar el archivo y retornar error
            os.remove(zip_path)
            return False, "El archivo descargado no es un archivo ZIP válido."

    except Exception as e:
        print(f"Error al descargar o extraer el ZIP: {e}")
        return False, f"Error al descargar o extraer el ZIP: {str(e)}"