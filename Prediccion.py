import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, Dense, Dropout
try:
    from tensorflow.keras.optimizers import Adam
except ImportError:
    # Fallback to standalone Keras if tensorflow.keras.optimizers is not available
    from keras.optimizers import Adam

# Lectura y filtrado (solo Municipio)
df = pd.read_csv('Atlantico.csv')
df.columns = df.columns.str.strip()

if 'Municipio' not in df.columns:
    raise KeyError("La columna 'Municipio' no existe en el CSV.")

mask = df['Municipio'].astype(str).str.contains('barranquilla', case=False, na=False)
f = df[mask].copy()

if f.empty:
    raise ValueError("No se encontraron filas de Barranquilla en 'Municipio'.")

# Preparar fechas y valores (un valor por día: primer ValorObservado válido)
if 'FechaObservacion' not in f.columns or 'ValorObservado' not in f.columns:
    raise KeyError("Faltan 'FechaObservacion' o 'ValorObservado' en el CSV.")

f['FechaObservacion'] = pd.to_datetime(f['FechaObservacion'], errors='coerce')
f = f.sort_values('FechaObservacion', ascending=True)
f['ValorObservado'] = pd.to_numeric(f['ValorObservado'], errors='coerce')
f = f.dropna(subset=['ValorObservado'])
f['Fecha'] = f['FechaObservacion'].dt.date
unico_por_dia = f.groupby('Fecha', sort=True, as_index=False).first()

# Eliminar filas cuyo ValorObservado sea 0 (no aportan información)
count_before = len(unico_por_dia)
unico_por_dia = unico_por_dia[unico_por_dia['ValorObservado'] != 0].copy()
removed = count_before - len(unico_por_dia)
if removed > 0:
    print(f"Se eliminaron {removed} día(s) con ValorObservado == 0")

if unico_por_dia.empty:
    raise ValueError("No quedan datos válidos después de eliminar ceros en 'ValorObservado'.")

valores = unico_por_dia['ValorObservado'].to_numpy().reshape(-1, 1)
print(f"Días disponibles (1 valor/día) tras eliminar ceros: {len(valores)}")

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
    raise ValueError("No hay suficientes datos para crear secuencias. Reduce 'pasos_atras' o use más datos.")

# Forma para RNN: (samples, timesteps, features)
X = X.reshape(X.shape[0], pasos_atras, 1)

# Dividir 80/20
train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# Modelo RNN (SimpleRNN)
model = Sequential([
    SimpleRNN(64, return_sequences=True, input_shape=(pasos_atras, 1), dropout=0.2, recurrent_dropout=0.1),
    SimpleRNN(32, return_sequences=False, dropout=0.2, recurrent_dropout=0.1),
    Dense(16, activation='relu'),
    Dropout(0.2),
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

# Función para predecir pasos futuros usando la última secuencia disponible
def predecir_futuro(model, secuencia_inicial_norm, pasos_futuros):
    preds = []
    seq = secuencia_inicial_norm.copy()
    for _ in range(pasos_futuros):
        p_norm = model.predict(seq.reshape(1, pasos_atras, 1))
        p_real = scaler.inverse_transform(p_norm)[0,0]
        preds.append(p_real)
        seq = np.append(seq[1:], p_norm).reshape(pasos_atras, 1)
    return preds

# Uso interactivo: pedir cuantos pasos futuros
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
plt.xlabel('Días (ordenados)')
plt.ylabel('Humedad (ValorObservado)')
plt.title('Predicción RNN - Humedad en Barranquilla (1 valor/día)')
plt.show()