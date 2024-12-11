from flask import Flask, session,jsonify
from routes import home
from routes import dueños
from routes import login
from routes import historial
from routes import historial_inquilinos
from routes import usuarios
from routes import versiones

app = Flask(__name__)

app.secret_key = "patatas" 

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
