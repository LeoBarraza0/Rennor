from flask import Blueprint, request, jsonify
from Prediccion import generar_prediccion
import os
import traceback
from datetime import datetime, timedelta

# Blueprint para rutas API
routes_Api = Blueprint('api', __name__)

@routes_Api.route('/prediccion', methods=['POST', 'OPTIONS'])
@routes_Api.route('/prediccion', methods=['POST', 'OPTIONS'])
def prediccion():
    """
    Endpoint para generar predicción RNN de humedad relativa
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        dias_futuros = int(data.get('dias_futuros', 7))
        
        if dias_futuros < 1 or dias_futuros > 30:
            return jsonify({
                'success': False,
                'error': 'El rango de días debe estar entre 1 y 30'
            }), 400
        
        csv_path = os.path.join('Config', 'static', 'Barranquilla_HR.csv')
        if not os.path.exists(csv_path):
            csv_path = 'Barranquilla_HR.csv'
        
        if not os.path.exists(csv_path):
            return jsonify({
                'success': False,
                'error': f'No se encontró el archivo CSV en {csv_path}'
            }), 404
        
        print(f"[PREDICCION] Generando predicción para {dias_futuros} días...")
        print(f"[PREDICCION] Usando archivo: {csv_path}")
        
        resultado = generar_prediccion(
            pasos_futuros=dias_futuros,
            csv_path=csv_path,
            verbose=1
        )
        
        predicciones = resultado['predicciones']
        metricas = resultado['metricas']
        
        if not predicciones:
            return jsonify({
                'success': False,
                'error': 'No se pudieron generar predicciones'
            }), 500
        
        hoy = datetime.now()
        fechas = [(hoy + timedelta(days=i+1)).strftime('%Y-%m-%d') for i in range(len(predicciones))]
        
        return jsonify({
            'success': True,
            'predicciones': predicciones,
            'dias': dias_futuros,
            'fechas': fechas,
            'metricas': {
                'mse': round(metricas['mse'], 2),
                'rmse': round(metricas['rmse'], 2),
                'mae': round(metricas['mae'], 2),
                'r_squared': round(metricas['r_squared'], 4)
            },
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except FileNotFoundError as e:
        print(f"[ERROR] Archivo no encontrado: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Archivo no encontrado: {str(e)}'
        }), 404
    
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
