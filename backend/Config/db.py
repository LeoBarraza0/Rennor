"""
Configuración de aplicación Flask para Rennor
"""
import os
from flask import Flask

# Obtener el directorio base del proyecto
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Crear aplicación Flask con el directorio base correcto
app = Flask(__name__)
app.secret_key = 'rennor-secret-key-change-in-production'

