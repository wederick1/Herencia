import os, time
import webbrowser
from flask import Flask, session
from routes import home, dueños, login, historial, historial_inquilinos, usuarios, versiones

app = Flask(__name__)
app.secret_key = "patatas"

# Registro de Blueprints
app.register_blueprint(home.bp)
app.register_blueprint(dueños.bp)
app.register_blueprint(login.bp)
app.register_blueprint(historial.bp)
app.register_blueprint(historial_inquilinos.bp)
app.register_blueprint(usuarios.bp)
app.register_blueprint(versiones.bp)

def abrir_navegador():
    url = "http://127.0.0.1:5000"
    print(f"Abriendo navegador en {url}...")
    webbrowser.open(url)

if __name__ == "__main__":
    abrir_navegador()
    time.sleep(2)  # Espera 2 segundos antes de iniciar el servidor
    app.run(debug=False)