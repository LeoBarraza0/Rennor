from flask import Blueprint, request, jsonify
import os
import traceback
import math
import numpy as np
from datetime import datetime
import logging

# Blueprint para rutas API
routes_Api = Blueprint('api', __name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@routes_Api.route('/prediccion', methods=['POST', 'OPTIONS'])
def prediccion():
    if request.method == 'OPTIONS':
        return ('', 204)

    try:
        data = request.get_json(silent=True) or {}
        dias_futuros = int(data.get('dias_futuros', 7))

        csv_paths = [
            os.path.join(os.getcwd(), 'Config', 'static', 'Barranquilla_HR.csv'),
            os.path.join(os.getcwd(), 'Barranquilla_HR.csv'),
            'Config/static/Barranquilla_HR.csv',
            'Barranquilla_HR.csv'
        ]
        csv_path = next((p for p in csv_paths if os.path.exists(p)), None)
        if csv_path is None:
            raise FileNotFoundError("CSV no encontrado en rutas esperadas")

        from Prediccion import generar_prediccion
        resultado = generar_prediccion(dias_futuros, csv_path=csv_path, verbose=0)

        # Función recursiva para sanitizar NaN/Inf y convertir tipos numpy a nativos
        def sanitize(obj):
            # dict -> sanitizar valores
            if isinstance(obj, dict):
                return {k: sanitize(v) for k, v in obj.items()}

            # numpy array -> convertir a lista y sanitizar
            if isinstance(obj, np.ndarray):
                return [sanitize(v) for v in obj.tolist()]

            # list/tuple -> sanitizar elemento a elemento
            if isinstance(obj, (list, tuple)):
                return [sanitize(v) for v in obj]

            # numpy scalar -> convertir a python native y sanitizar
            if isinstance(obj, np.generic):
                return sanitize(obj.item())

            # floats: reemplazar NaN/Inf por None
            if isinstance(obj, float):
                if math.isnan(obj) or math.isinf(obj):
                    return None
                return float(obj)

            # ints/bools/strs ya son serializables
            if isinstance(obj, (int, bool, str)):
                return obj

            # fallback: intentar convertir tipos numéricos de numpy (ej. numpy.int64)
            try:
                if hasattr(obj, 'item'):
                    return sanitize(obj.item())
            except Exception:
                pass

            # si no se reconoce el tipo, devolverlo tal cual (Flask/jsonify lo convertirá o fallará)
            return obj

        safe_result = sanitize(resultado)
        # Asegurar que la respuesta incluya un indicador de éxito para el frontend
        if isinstance(safe_result, dict):
            safe_result.setdefault('success', True)
        else:
            safe_result = {'success': True, 'data': safe_result}

        logger.info("Predicción generada exitosamente")
        return jsonify(safe_result), 200

    except FileNotFoundError as e:
        logger.error(str(e))
        return jsonify({"error": str(e)}), 404

    except ValueError as e:
        logger.error(str(e))
        return jsonify({"error": str(e)}), 400
    
    except ValueError as e:
        print(f"[ERROR] Validación: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error en datos: {str(e)}'
        }), 400
    
    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }), 500

@routes_Api.route('/datos-historicos', methods=['GET', 'OPTIONS'])
def datos_historicos():
    """
    Endpoint para cargar información de datos históricos
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        import pandas as pd
        
        csv_path = os.path.join('Config', 'static', 'Barranquilla_HR.csv')
        if not os.path.exists(csv_path):
            csv_path = 'Barranquilla_HR.csv'
        
        if not os.path.exists(csv_path):
            return jsonify({
                'success': False,
                'error': 'Archivo CSV no encontrado'
            }), 404
        
        df = pd.read_csv(csv_path, sep=';')
        total = len(df)
        
        return jsonify({
            'success': True,
            'total': total,
            'mensaje': f'Se cargaron {total} registros históricos'
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al cargar datos: {str(e)}'
        }), 500

@routes_Api.route('/info-rnn', methods=['GET'])
def info_rnn():
    """
    Endpoint para obtener información sobre la arquitectura RNN
    """
    return jsonify({
        'success': True,
        'info': {
            'tipo': 'Recurrent Neural Network (SimpleRNN)',
            'capas': 2,
            'arquitectura': {
                'capa_1': {
                    'tipo': 'SimpleRNN',
                    'neuronas': 64,
                    'dropout': 0.1,
                    'recurrent_dropout': 0.05
                },
                'capa_2': {
                    'tipo': 'SimpleRNN',
                    'neuronas': 32,
                    'dropout': 0.1,
                    'recurrent_dropout': 0.05
                },
                'dense_1': {
                    'tipo': 'Dense',
                    'neuronas': 16,
                    'activacion': 'relu'
                },
                'output': {
                    'tipo': 'Dense',
                    'neuronas': 1,
                    'activacion': 'linear'
                }
            },
            'parametros_entrenamiento': {
                'optimizador': 'Adam',
                'learning_rate': 0.001,
                'loss': 'MSE',
                'epochs': 50,
                'batch_size': 8
            },
            'datos': {
                'dataset': 'Humedad Relativa Barranquilla',
                'separador_datos': '80% entrenamiento / 20% validación',
                'normalizacion': 'MinMaxScaler (0-1)',
                'lookback': 5
            },
            'descripcion': 'Red neuronal recurrente entrenada para predecir humedad relativa futura basándose en valores históricos'
        }
    }), 200

@routes_Api.route('/health', methods=['GET'])
def health():
    """
    Endpoint para verificar que el servidor está activo
    """
    return jsonify({
        'status': 'ok',
        'service': 'RENNOR API',
        'timestamp': datetime.now().isoformat()
    }), 200
