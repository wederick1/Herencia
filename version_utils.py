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
    Descarga un archivo ZIP y lo extrae, manteniendo su estructura de carpetas.
    """
    try:
        # Crear la carpeta de salida si no existe
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        zip_path = os.path.join(output_folder, file_name)

        # Descargar el archivo ZIP
        response = requests.get(asset_url)
        response.raise_for_status()

        # Guardar el archivo ZIP en el sistema
        with open(zip_path, 'wb') as f:
            f.write(response.content)

        # Verificar que el archivo fue descargado
        if not os.path.exists(zip_path):
            raise FileNotFoundError(f"El archivo {zip_path} no se pudo descargar correctamente.")

        # Crear carpeta para extraer los archivos
        extract_path = os.path.join(output_folder, 'versiones')
        if not os.path.exists(extract_path):
            os.makedirs(extract_path)

        # Verificar si el archivo descargado es un ZIP válido
        if zipfile.is_zipfile(zip_path):
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            # Eliminar el archivo ZIP después de la extracción
            os.remove(zip_path)

            return True, f"Archivo ZIP descargado y extraído correctamente en {extract_path}."
        else:
            # Si no es un ZIP válido, eliminar el archivo descargado
            os.remove(zip_path)
            return False, "El archivo descargado no es un ZIP válido."

    except requests.RequestException as e:
        return False, f"Error al descargar el archivo: {str(e)}"

    except FileNotFoundError as e:
        return False, f"Archivo no encontrado: {str(e)}"

    except zipfile.BadZipFile:
        return False, "El archivo descargado no es un archivo ZIP válido."

    except Exception as e:
        return False, f"Error al descargar o extraer el ZIP: {str(e)}"  
