"""
Aplicación principal de RENNOR
API REST para predicción de humedad relativa usando RNN
"""
from flask import Flask, jsonify
from flask_cors import CORS
from Config.db import app as flask_app
from Config.Controller.ApiController import routes_Api
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Usar la app de Config.db
app = flask_app

# Configurar CORS para permitir conexiones desde el frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Registrar blueprints
app.register_blueprint(routes_Api, url_prefix='/api')

@app.route('/', methods=['GET'])
def index():
    """Health check del servidor"""
    return jsonify({
        'status': 'ok',
        'service': 'RENNOR Backend API',
        'version': '1.0'
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    print(f"\n{'='*50}")
    print(f"RENNOR Backend iniciado")
    print(f"URL: http://localhost:{port}")
    print(f"CORS habilitado para: http://localhost:3000")
    print(f"{'='*50}\n")
    app.run(debug=True, host='0.0.0.0', port=port)