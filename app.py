import os
from flask import Flask, session, jsonify, render_template
from routes import home, dueños, login, historial, historial_inquilinos, usuarios, versiones
from version_utils import obtener_releases  # Importa desde el nuevo archivo
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)

app.secret_key = "patatas" 

# Configura la versión actual en la sesión
@app.before_request
def set_version_in_session():
    # Establecer la versión actual, esta puede ser la que quieras o obtenerla de un archivo de configuración
    session['current_version'] = "1.0.0"  # Aquí puedes poner la versión real

# Ruta para obtener la versión actual
@app.route('/get_current_version')
def get_current_version():
    # Regresa la versión actual almacenada en la sesión
    return jsonify({"current_version": session.get('current_version', 'Unknown')})
  


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
