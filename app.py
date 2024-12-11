from flask import Flask, session, jsonify, render_template
from routes import home
from routes import dueños
from routes import login
from routes import historial
from routes import historial_inquilinos
from routes import usuarios
from routes import versiones
from apscheduler.schedulers.background import BackgroundScheduler
import requests

app = Flask(__name__)

app.secret_key = "patatas" 

# Variables globales
last_commit = None
GITHUB_API_URL = "https://api.github.com/repos/wederick1/Herencia/commits"

@app.context_processor
def inject_user_initial():
    username = session.get('username', '')
    nombre = username[0].upper() if username else ''  # Obtener la inicial
    return {'user_initial': nombre}

@app.route('/check_session', methods=['GET'])
def check_session():
    # Verificar si el usuario está logueado
    if 'username' in session:
        return jsonify({'logged_in': True, 'username': session['username']})
    else:
        return jsonify({'logged_in': False}), 401

# Verificar si hay cambios en el repositorio
def check_for_updates():
    global last_commit
    try:
        # Obtener los commits más recientes
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()  # Lanzará un error si la respuesta no es exitosa

        # Extraemos el hash del último commit
        latest_commit = response.json()[0]["sha"]
        
        if latest_commit != last_commit:
            # Si el commit ha cambiado, significa que hay una nueva versión
            print("¡Nueva versión disponible!")
            last_commit = latest_commit  # Actualizamos el commit más reciente
            return True
        else:
            return False
    except Exception as e:
        print(f"Error al consultar GitHub: {e}")
        return False

# Iniciar el scheduler para revisar los cambios cada 30 minutos
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_for_updates, trigger="interval", minutes=30)
scheduler.start()

@app.route('/')
def index():
    # Comprobamos si hay una nueva versión
    new_version = check_for_updates()
    return render_template('index.html', new_version=new_version)

# Registro de Blueprints
app.register_blueprint(home.bp)
app.register_blueprint(dueños.bp)
app.register_blueprint(login.bp)
app.register_blueprint(historial.bp)
app.register_blueprint(historial_inquilinos.bp)
app.register_blueprint(usuarios.bp)
app.register_blueprint(versiones.bp)

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
