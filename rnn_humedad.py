# Redes neuronales RNN para Predicción de Humedad Relativa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, Dense, Dropout
from tensorflow.keras.optimizers import Adam

# 1. CARGAR DATOS DESDE ARCHIVO EXCEL
print("📂 Cargando datos desde archivo Excel...")

# Solicitar nombre del archivo
nombre_archivo = input("Ingrese el nombre del archivo Excel (ej: datos_humedad.xlsx): ")

try:
    df = pd.read_excel(nombre_archivo)
    print(f"✅ Se extrajeron {len(df)} registros desde el archivo")
except FileNotFoundError:
    print(f"❌ Error: No se encontró el archivo '{nombre_archivo}'")
    print("💡 Asegúrate de que el archivo esté en la misma carpeta que este script")
    exit()
except Exception as e:
    print(f"❌ Error al cargar el archivo: {e}")
    exit()

# 2. PREPROCESAR DATOS
print("🔄 Procesando datos...")

# Renombrar columnas para facilitar el trabajo
df.columns = df.columns.str.strip()  # Eliminar espacios
columnas_map = {
    'FechaObservacion': 'fecha',
    'ValorObservado': 'valor'
}

# Buscar las columnas correctas (por si tienen nombres ligeramente diferentes)
for col in df.columns:
    if 'fecha' in col.lower():
        columnas_map[col] = 'fecha'
    elif 'valor' in col.lower() and 'observ' in col.lower():
        columnas_map[col] = 'valor'

df = df.rename(columns=columnas_map)

# Convertir fecha a datetime
df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')

# Convertir valor a numérico
df['valor'] = pd.to_numeric(df['valor'], errors='coerce')

# Eliminar valores nulos
df_limpio = df.dropna(subset=['fecha', 'valor'])

print(f"✅ Registros válidos después de limpieza: {len(df_limpio)}")

# 3. AGRUPAR POR DÍA (Promedio diario)
print("📅 Agrupando datos por día (calculando promedio diario)...")

df_limpio['fecha_dia'] = df_limpio['fecha'].dt.date
df_diario = df_limpio.groupby('fecha_dia')['valor'].mean().reset_index()
df_diario.columns = ['fecha', 'humedad_promedio']

# Ordenar por fecha
df_diario = df_diario.sort_values('fecha')

# Extraer valores de humedad
humedad = df_diario['humedad_promedio'].values

print(f"✅ Se procesaron {len(humedad)} días de datos")
print(f"📊 Rango de humedad: {humedad.min():.2f}% - {humedad.max():.2f}%")
print(f"📅 Periodo: {df_diario['fecha'].min()} a {df_diario['fecha'].max()}")
print(f"\n⏱️  NOTA: Cada registro representa un día. Las predicciones son por día.")

# Eliminar valores NaN
humedad = humedad[~np.isnan(humedad)]

# Convertir a array de NumPy y reformatear
valores = humedad.reshape(-1, 1)

# 4. Normalizar los datos entre 0 y 1
scaler = MinMaxScaler(feature_range=(0, 1))
valores_normalizados = scaler.fit_transform(valores)

# 5. Crear secuencias para la RNN
def crear_secuencias(data, pasos):
    X, y = [], []
    for i in range(len(data) - pasos):
        X.append(data[i:i+pasos])
        y.append(data[i+pasos])
    return np.array(X), np.array(y)

pasos_atras = 7  # Número de días atrás para predecir (1 semana)
X, y = crear_secuencias(valores_normalizados, pasos_atras)

# Cambiar la forma de los datos para la RNN
X = X.reshape(X.shape[0], pasos_atras, 1)

print(f"\n📦 Secuencias creadas: {len(X)} secuencias de {pasos_atras} días cada una")

# Dividir en entrenamiento y prueba (80% - 20%)
train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

print(f"🔹 Datos de entrenamiento: {len(X_train)} secuencias")
print(f"🔹 Datos de prueba: {len(X_test)} secuencias")

# 6. Construir la red RNN Optimizada
model = Sequential([
    SimpleRNN(64, return_sequences=True, input_shape=(pasos_atras, 1), recurrent_dropout=0.2),
    SimpleRNN(64, return_sequences=True, dropout=0.2, recurrent_dropout=0.2),
    SimpleRNN(32, return_sequences=False, dropout=0.2, recurrent_dropout=0.2),
    Dense(32, activation='relu'),
    Dropout(0.2),
    Dense(1, activation='linear')
])

# 📌 Agregar Resumen del Modelo
print("\n" + "="*60)
print("🧠 ARQUITECTURA DE LA RED NEURONAL RNN")
print("="*60)
model.summary()

# Compilar el modelo con optimizador Adam y tasa de aprendizaje ajustada
model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')

# 7. Entrenar el modelo
print("\n" + "="*60)
print("🔄 ENTRENANDO EL MODELO...")
print("="*60)
print("⏳ Esto puede tomar varios minutos dependiendo de la cantidad de datos...\n")

history = model.fit(X_train, y_train, 
                   epochs=30, 
                   batch_size=32, 
                   validation_data=(X_test, y_test),
                   verbose=1)

# 8. Hacer predicciones
print("\n🔮 Realizando predicciones...")
predicciones = model.predict(X_test, verbose=0)
predicciones = scaler.inverse_transform(predicciones)  # Desnormalizar

# 9. Calcular métricas de error
mse = mean_squared_error(valores[train_size+pasos_atras:], predicciones)
rmse = np.sqrt(mse)
mae = mean_absolute_error(valores[train_size+pasos_atras:], predicciones)

print("\n" + "="*60)
print("📊 MÉTRICAS DEL MODELO OPTIMIZADO")
print("="*60)
print(f"🔹 MSE  (Error Cuadrático Medio): {mse:.4f}")
print(f"🔹 RMSE (Raíz del Error Cuadrático Medio): {rmse:.4f}")
print(f"🔹 MAE  (Error Absoluto Medio): {mae:.4f}")
print(f"🔹 Precisión promedio: ±{mae:.2f}%")

# 10. Predicción de futuros valores
def predecir_futuro(model, secuencia_inicial, pasos_futuros):
    predicciones_futuras = []
    secuencia_actual = secuencia_inicial.copy()

    for _ in range(pasos_futuros):
        prediccion = model.predict(secuencia_actual.reshape(1, pasos_atras, 1), verbose=0)
        prediccion_real = scaler.inverse_transform(prediccion)[0, 0]
        predicciones_futuras.append(prediccion_real)

        # Agregar nueva predicción y eliminar la más antigua
        secuencia_actual = np.append(secuencia_actual[1:], prediccion).reshape(pasos_atras, 1)

    return predicciones_futuras

# 🔹 Usuario ingresa el número de días a predecir
print("\n" + "="*60)
pasos_futuros = int(input("\n¿Cuántos días en el futuro deseas predecir?: "))
secuencia_inicial = valores_normalizados[-pasos_atras:]  # Últimos valores para predecir

predicciones_futuras = predecir_futuro(model, secuencia_inicial, pasos_futuros)

# 11. Graficar resultados
plt.figure(figsize=(16, 7))

# Gráfica principal
plt.subplot(1, 2, 1)
plt.plot(range(len(valores)), valores, label="Datos reales", color="blue", linewidth=1.5, alpha=0.7)
plt.plot(range(train_size+pasos_atras, train_size+pasos_atras+len(predicciones)), predicciones,
         label="Predicción (validación)", linestyle="dashed", color="red", linewidth=2)
plt.plot(range(len(valores), len(valores)+pasos_futuros), predicciones_futuras,
         label="Predicción futura", linestyle="dotted", color="green", linewidth=2, marker='o', markersize=4)
plt.axvline(x=train_size+pasos_atras, color='gray', linestyle='--', alpha=0.5, label='Inicio validación')
plt.legend()
plt.xlabel("Tiempo (días)")
plt.ylabel("Humedad Relativa (%)")
plt.title("Predicción de Humedad Relativa con RNN")
plt.grid(True, alpha=0.3)

# Gráfica de zoom en predicciones futuras
plt.subplot(1, 2, 2)
ultimos_dias = 30  # Mostrar últimos 30 días
plt.plot(range(len(valores)-ultimos_dias, len(valores)), valores[-ultimos_dias:], 
         label="Datos reales (últimos días)", color="blue", linewidth=2, marker='o', markersize=3)
plt.plot(range(len(valores), len(valores)+pasos_futuros), predicciones_futuras,
         label="Predicción futura", linestyle="dotted", color="green", linewidth=2, marker='o', markersize=5)
plt.legend()
plt.xlabel("Tiempo (días)")
plt.ylabel("Humedad Relativa (%)")
plt.title(f"Zoom: Últimos {ultimos_dias} días + Predicción")
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Mostrar valores futuros predichos
print("\n" + "="*60)
print(f"📈 PREDICCIÓN PARA LOS PRÓXIMOS {pasos_futuros} DÍAS")
print("="*60)
for i, pred in enumerate(predicciones_futuras, 1):
    print(f"  Día +{i}: {pred:.2f}%")

# 12. 🔹 Permitir al usuario ingresar un dato y predecir su resultado 🔹
print("\n" + "="*60)
print("🔧 PREDICCIÓN CON DATO PERSONALIZADO")
print("="*60)
print("Ingresa valores de humedad para ver la predicción del siguiente día")

while True:
    try:
        entrada = input("\nIngrese un valor de humedad (%) o 'salir' para terminar: ")
        if entrada.lower() == 'salir':
            break
        nuevo_dato = float(entrada)
    except ValueError:
        print("✅ Fin de la predicción.")
        break

    # Validar rango
    if nuevo_dato < 0 or nuevo_dato > 100:
        print("⚠️  La humedad debe estar entre 0 y 100%")
        continue

    # Normalizar el nuevo dato
    nuevo_dato_norm = scaler.transform(np.array([[nuevo_dato]]))

    # Tomar los últimos datos y agregar el nuevo valor
    secuencia_usuario = np.append(valores_normalizados[-(pasos_atras-1):], nuevo_dato_norm).reshape(pasos_atras, 1)

    # Predecir el siguiente valor
    prediccion_usuario = model.predict(secuencia_usuario.reshape(1, pasos_atras, 1), verbose=0)
    prediccion_usuario_real = scaler.inverse_transform(prediccion_usuario)[0, 0]

    print(f"🔮 Predicción para el día siguiente: {prediccion_usuario_real:.2f}%")

print("\n🎉 Gracias por usar el sistema de predicción de humedad relativa!")
print("="*60)