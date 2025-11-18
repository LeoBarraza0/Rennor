import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import os

# Función para generar predicción
def generar_prediccion(pasos_futuros, csv_path=None, verbose=0):
    """
    Genera predicción usando la lógica de Prediccion.py
    Args:
        pasos_futuros: número de pasos a predecir
        csv_path: ruta al CSV (si None, busca en ubicaciones comunes)
        verbose: 0=silencioso, 1=normal, 2=detallado
    Returns:
        lista de predicciones
    """
    # Determinar ruta del CSV
    if csv_path is None:
        csv_path = 'Barranquilla_HR.csv'
        if not os.path.exists(csv_path):
            csv_path = os.path.join('Config', 'static', 'Barranquilla_HR.csv')
    
    # Verificar que el archivo existe
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f'No se encontró el archivo CSV en: {csv_path}')
    
    # Lectura de datos limpios
    df = pd.read_csv(csv_path, sep=';')
    df['FechaObservacion'] = pd.to_datetime(df['FechaObservacion'], errors='coerce')
    df = df.sort_values('FechaObservacion', ascending=True)
    df = df.dropna(subset=['ValorObservado'])

    # Eliminar valores == 0
    count_before = len(df)
    df = df[df['ValorObservado'] != 0].copy()
    removed = count_before - len(df)
    if removed > 0 and verbose > 0:
        print(f"Se eliminaron {removed} registro(s) con ValorObservado == 0")

    if df.empty:
        raise ValueError("No quedan datos válidos después de eliminar ceros.")

    valores = df['ValorObservado'].to_numpy().reshape(-1, 1)
    if verbose > 0:
        print(f"Registros disponibles: {len(valores)}")

    # Normalizar
    scaler = MinMaxScaler((0, 1))
    valores_norm = scaler.fit_transform(valores)

    # Crear secuencias
    def crear_secuencias(data, pasos):
        X, y = [], []
        for i in range(len(data) - pasos):
            X.append(data[i:i+pasos])
            y.append(data[i+pasos])
        return np.array(X), np.array(y)

    pasos_atras = 5
    X, y = crear_secuencias(valores_norm, pasos_atras)
    if len(X) == 0:
        raise ValueError("No hay suficientes datos para crear secuencias.")

    X = X.reshape(X.shape[0], pasos_atras, 1)

    # Dividir 80/20
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # Modelo RNN
    model = Sequential([
        SimpleRNN(64, return_sequences=True, input_shape=(pasos_atras, 1), dropout=0.1, recurrent_dropout=0.05),
        SimpleRNN(32, return_sequences=False, dropout=0.1, recurrent_dropout=0.05),
        Dense(16, activation='relu'),
        Dropout(0.1),
        Dense(1, activation='linear')
    ])

    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
    if verbose > 0:
        model.summary()

    # Entrenamiento
    epochs = 50
    batch_size = 8
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_test, y_test), verbose=verbose)

    # Predicción y métricas
    pred_norm = model.predict(X_test, verbose=0)
    pred = scaler.inverse_transform(pred_norm)
    y_test_real = scaler.inverse_transform(y_test)

    mse = mean_squared_error(y_test_real, pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test_real, pred)

    if verbose > 0:
        print(f"\nMSE: {mse:.4f}  RMSE: {rmse:.4f}  MAE: {mae:.4f}")

    # Predicción futura
    def predecir_futuro(model, secuencia_inicial_norm, pasos_futuros):
        preds = []
        seq = secuencia_inicial_norm.copy()
        for _ in range(pasos_futuros):
            p_norm = model.predict(seq.reshape(1, pasos_atras, 1), verbose=0)
            p_real = scaler.inverse_transform(p_norm)[0,0]
            preds.append(float(p_real))
            seq = np.append(seq[1:], p_norm).reshape(pasos_atras, 1)
        return preds

    if pasos_futuros > 0:
        secuencia_inicial = valores_norm[-pasos_atras:].reshape(pasos_atras, 1)
        futuros = predecir_futuro(model, secuencia_inicial, pasos_futuros)
        return futuros
    return []

# Código que se ejecuta solo cuando se corre el script directamente
if __name__ == "__main__":
    # Lectura de datos limpios
    df = pd.read_csv('Barranquilla_HR.csv', sep=';')
    df['FechaObservacion'] = pd.to_datetime(df['FechaObservacion'], errors='coerce')
    df = df.sort_values('FechaObservacion', ascending=True)
    df = df.dropna(subset=['ValorObservado'])

    # Eliminar valores == 0
    count_before = len(df)
    df = df[df['ValorObservado'] != 0].copy()
    removed = count_before - len(df)
    if removed > 0:
        print(f"Se eliminaron {removed} registro(s) con ValorObservado == 0")

    if df.empty:
        raise ValueError("No quedan datos válidos después de eliminar ceros.")

    valores = df['ValorObservado'].to_numpy().reshape(-1, 1)
    print(f"Registros disponibles: {len(valores)}")

    # Normalizar
    scaler = MinMaxScaler((0, 1))
    valores_norm = scaler.fit_transform(valores)

    # Crear secuencias
    def crear_secuencias(data, pasos):
        X, y = [], []
        for i in range(len(data) - pasos):
            X.append(data[i:i+pasos])
            y.append(data[i+pasos])
        return np.array(X), np.array(y)

    pasos_atras = 5
    X, y = crear_secuencias(valores_norm, pasos_atras)
    if len(X) == 0:
        raise ValueError("No hay suficientes datos para crear secuencias.")

    X = X.reshape(X.shape[0], pasos_atras, 1)

    # Dividir 80/20
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # Modelo RNN
    model = Sequential([
        SimpleRNN(64, return_sequences=True, input_shape=(pasos_atras, 1), dropout=0.1, recurrent_dropout=0.05),
        SimpleRNN(32, return_sequences=False, dropout=0.1, recurrent_dropout=0.05),
        Dense(16, activation='relu'),
        Dropout(0.1),
        Dense(1, activation='linear')
    ])

    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
    model.summary()

    # Entrenamiento
    epochs = 50
    batch_size = 8
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_test, y_test), verbose=2)

    # Predicción y métricas
    pred_norm = model.predict(X_test)
    pred = scaler.inverse_transform(pred_norm)
    y_test_real = scaler.inverse_transform(y_test)

    mse = mean_squared_error(y_test_real, pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test_real, pred)

    print(f"\nMSE: {mse:.4f}  RMSE: {rmse:.4f}  MAE: {mae:.4f}")

    # Predicción futura
    def predecir_futuro(model, secuencia_inicial_norm, pasos_futuros):
        preds = []
        seq = secuencia_inicial_norm.copy()
        for _ in range(pasos_futuros):
            p_norm = model.predict(seq.reshape(1, pasos_atras, 1), verbose=0)
            p_real = scaler.inverse_transform(p_norm)[0,0]
            preds.append(p_real)
            seq = np.append(seq[1:], p_norm).reshape(pasos_atras, 1)
        return preds

    try:
        pasos_futuros = int(input("¿Cuántos pasos en el futuro deseas predecir?: "))
    except Exception:
        pasos_futuros = 0

    if pasos_futuros > 0:
        secuencia_inicial = valores_norm[-pasos_atras:].reshape(pasos_atras, 1)
        futuros = predecir_futuro(model, secuencia_inicial, pasos_futuros)
        print("Predicciones futuras:", futuros)

    # Gráfica
    plt.figure(figsize=(10,5))
    plt.plot(range(len(valores)), valores, label='Datos reales')
    start_pred = train_size + pasos_atras
    plt.plot(range(start_pred, start_pred + len(pred)), pred, linestyle='--', color='red', label='Predicción test')
    if pasos_futuros > 0:
        plt.plot(range(len(valores), len(valores) + len(futuros)), futuros, linestyle=':', color='green', label='Predicción futura')
    plt.legend()
    plt.xlabel('Registros (ordenados)')
    plt.ylabel('Humedad (ValorObservado)')
    plt.title('Predicción RNN - Humedad en Barranquilla')
    plt.show()