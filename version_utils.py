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

            # Determinar el último release no preliminar
            if not release["prerelease"] and (not latest_release or release_date > datetime.strptime(latest_release["created_at"], "%Y-%m-%dT%H:%M:%SZ")):
                latest_release = release

        # Leer la versión actual desde el archivo 'Version_details.txt'
        try:
            detalles_actuales = leer_detalles_version()
            version_actual = detalles_actuales["nombre"] if detalles_actuales["nombre"] else None
        except FileNotFoundError:
            version_actual = None  # Si no hay archivo, se asume que no hay una versión instalada

        # Comprobar si hay una nueva versión disponible
        if latest_release:
            version_github = latest_release["name"]
            if version_actual is None or version_actual != version_github:
                new_version_available = True

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



def leer_detalles_version():
    """
    Lee los detalles de la versión desde el archivo 'Version_details.txt' ubicado en el nivel raíz de la aplicación.

    Returns:
        dict: Un diccionario con los detalles de la versión, incluyendo nombre, descripción y fecha.

    Raises:
        FileNotFoundError: Si el archivo 'Version_details.txt' no existe.
        ValueError: Si faltan datos o el archivo tiene un formato incorrecto.
    """
    # Construir la ruta absoluta del archivo
    ruta_archivo = os.path.join(os.path.abspath(os.path.dirname(__file__)), "Version_details.txt")

    # Inicializar los detalles de la versión
    detalles = {
        "nombre": None,
        "descripcion": None,
        "fecha": None,
    }

    try:
        # Leer el archivo línea por línea
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                # Dividir la línea en clave y valor
                if ":" in linea:
                    clave, valor = map(str.strip, linea.split(":", 1))
                    if clave == "Nombre de la versión":
                        detalles["nombre"] = valor
                    elif clave == "Descripción":
                        detalles["descripcion"] = valor
                    elif clave == "Fecha de creación":
                        detalles["fecha"] = valor

        # Validar que todos los detalles hayan sido encontrados
        if not all(detalles.values()):
            raise ValueError("El archivo 'Version_details.txt' no contiene todos los campos requeridos.")

        return detalles

    except FileNotFoundError:
        raise FileNotFoundError(f"El archivo 'Version_details.txt' no fue encontrado en la ruta: {ruta_archivo}")
    except Exception as e:
        raise RuntimeError(f"Error al leer los detalles de la versión: {str(e)}")
