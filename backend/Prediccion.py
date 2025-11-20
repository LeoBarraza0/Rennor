import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import os

def generar_prediccion(pasos_futuros, csv_path=None, verbose=0):
    # Copia literal del flujo del bloque main adaptada a función
    # Fuente de datos (forzamos la misma ruta que el main si no se pasa csv_path)
    if csv_path is None:
        csv_path = 'Config/Barranquilla_HR.csv'
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f'No se encontró el archivo CSV en: {csv_path}')

    df = pd.read_csv(csv_path, sep=';')
    df['FechaObservacion'] = pd.to_datetime(df['FechaObservacion'], errors='coerce')
    df = df.sort_values('FechaObservacion', ascending=True)
    df = df.dropna(subset=['ValorObservado'])

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

    scaler = MinMaxScaler((0, 1))
    valores_norm = scaler.fit_transform(valores)

    def crear_secuencias(data, pasos):
        X, y = [], []
        for i in range(len(data) - pasos):
            X.append(data[i:i+pasos])
            y.append(data[i+pasos])
        return np.array(X), np.array(y)

    # Aumentamos ligeramente la ventana temporal para capturar más contexto
    pasos_atras = 8
    X, y = crear_secuencias(valores_norm, pasos_atras)
    if len(X) == 0:
        raise ValueError("No hay suficientes datos para crear secuencias.")
    X = X.reshape(X.shape[0], pasos_atras, 1)

    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    model = Sequential([
        SimpleRNN(64, return_sequences=True, input_shape=(pasos_atras, 1)),
        SimpleRNN(48, return_sequences=False),
        Dense(24, activation='relu'),
        Dense(1, activation='linear')
    ])
    model.compile(optimizer=Adam(learning_rate=0.0007), loss='mse')
    if verbose > 0:
        model.summary()

    epochs = 200
    batch_size = 8
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=12, restore_best_weights=True),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=6, min_lr=1e-5, verbose=0)
    ]
    model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_test, y_test),
        callbacks=callbacks,
        verbose=verbose
    )

    pred_norm = model.predict(X_test)
    pred = scaler.inverse_transform(pred_norm)
    y_test_real = scaler.inverse_transform(y_test)

    mse = mean_squared_error(y_test_real, pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test_real, pred)
    ss_res = np.sum((y_test_real - pred) ** 2)
    ss_tot = np.sum((y_test_real - np.mean(y_test_real)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
    if verbose > 0:
        print(f"\nMSE: {mse:.4f}  RMSE: {rmse:.4f}  MAE: {mae:.4f}")

    # Preparar datos comparación (idéntico a main)
    indice_inicio_test = train_size + pasos_atras
    fechas_originales = df['FechaObservacion'].dt.strftime('%Y-%m-%d').astype(str).tolist()
    fechas_comparacion = fechas_originales[indice_inicio_test:indice_inicio_test + len(y_test_real)]
    valores_reales_comparacion = y_test_real.flatten().tolist()
    valores_predichos_comparacion = pred.flatten().tolist()

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
    predicciones = []
    if pasos_futuros > 0:
        secuencia_inicial = valores_norm[-pasos_atras:].reshape(pasos_atras, 1)
        predicciones = predecir_futuro(model, secuencia_inicial, pasos_futuros)

    # Historial (downsampling igual que antes)
    historial_fechas = fechas_originales.copy()
    historial_valores = valores.flatten().tolist()
    def downsample_list(lst, max_points=1200):
        n = len(lst)
        if n <= max_points:
            return lst
        indices = np.linspace(0, n - 1, max_points).round().astype(int)
        return [lst[i] for i in indices]
    max_hist_points = 1200
    historial_down_fechas = downsample_list(historial_fechas, max_points=max_hist_points)
    historial_down_valores = downsample_list(historial_valores, max_points=max_hist_points)

    return {
        'predicciones': predicciones,
        'metricas': {
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'r_squared': float(r_squared)
        },
        'datos_comparacion': {
            'fechas_pasadas': fechas_comparacion,
            'valores_reales': valores_reales_comparacion,
            'valores_predichos': valores_predichos_comparacion
        },
        'historial': {
            'fechas': historial_down_fechas,
            'valores': historial_down_valores,
            'original_length': len(historial_fechas)
        }
    }

if __name__ == "__main__":
    # Lectura de datos limpios
    df = pd.read_csv('Config/Barranquilla_HR.csv', sep=';')
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

    pasos_atras = 8
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
        SimpleRNN(64, return_sequences=True, input_shape=(pasos_atras, 1)),
        SimpleRNN(48, return_sequences=False),
        Dense(24, activation='relu'),
        Dense(1, activation='linear')
    ])

    model.compile(optimizer=Adam(learning_rate=0.0007), loss='mse')
    model.summary()

    # Entrenamiento
    epochs = 200
    batch_size = 8
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=12, restore_best_weights=True),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=6, min_lr=1e-5, verbose=1)
    ]
    model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_test, y_test),
        callbacks=callbacks,
        verbose=2
    )

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