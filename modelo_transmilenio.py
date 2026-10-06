# ===============================================================
# Modelo de aprendizaje supervisado - Transmilenio
# Objetivo: predecir el TIEMPO REAL de viaje (minutos) entre dos
# estaciones consecutivas (problema de REGRESIÓN).
# Ejecución:  python modelo_transmilenio.py
# Requisitos: pip install pandas numpy scikit-learn matplotlib joblib
# ===============================================================

import random
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # permite guardar gráficas sin abrir ventanas
import matplotlib.pyplot as plt
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Semillas para que los resultados sean reproducibles
random.seed(42)
np.random.seed(42)

# ---------------------------------------------------------------
# 1. HECHOS DEL PROYECTO ORIGINAL (tiempo base entre estaciones)
# ---------------------------------------------------------------
Hechos = [
    ("Portal Norte", "Toberín", 4), ("Toberín", "Calle 146", 3),
    ("Calle 146", "Pepe Sierra", 4), ("Pepe Sierra", "Calle 100", 3),
    ("Calle 100", "Héroes", 5), ("Héroes", "Calle 72", 3),
    ("Calle 72", "Calle 45", 5), ("Calle 45", "Calle 26", 4),
    ("Calle 26", "Av. Jiménez", 4), ("Av. Jiménez", "Tercer Milenio", 3),
    ("Av. Jiménez", "De La Sabana", 3), ("De La Sabana", "Ricaurte", 4),
    ("Ricaurte", "Pradera", 5), ("Pradera", "Banderas", 6),
    ("Banderas", "Portal Américas", 5), ("Calle 26", "Centro Memoria", 3),
    ("Centro Memoria", "CAD", 4), ("CAD", "Av. Rojas", 6),
    ("Av. Rojas", "Portal El Dorado", 5), ("Ricaurte", "Paloquemao", 3),
    ("Paloquemao", "CAD", 5),
]

# ---------------------------------------------------------------
# 2. GENERACIÓN DEL DATASET SINTÉTICO
# Cada fila simula un viaje entre dos estaciones conectadas.
# ---------------------------------------------------------------
def generar_dataset(n=3000):
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    filas = []
    for _ in range(n):
        origen, destino, t_base = random.choice(Hechos)
        if random.random() < 0.5:              # la ruta también se recorre al revés
            origen, destino = destino, origen
        dia = random.choice(dias)
        hora = random.randint(5, 22)
        es_laboral = dia not in ("Sábado", "Domingo")
        hora_pico = 1 if es_laboral and (6 <= hora <= 9 or 17 <= hora <= 19) else 0
        lluvia = random.choices([0, 1], weights=[0.75, 0.25])[0]
        pasajeros = max(int(np.random.normal(300 if hora_pico else 120, 40)), 10)

        # Relación "oculta" que el modelo debe aprender:
        # el tiempo sube con hora pico, lluvia y cantidad de pasajeros
        tiempo = t_base * (1 + 0.35 * hora_pico + 0.10 * lluvia + pasajeros / 2000)
        tiempo += np.random.normal(0, 0.4)     # ruido aleatorio
        filas.append([origen, destino, dia, hora, hora_pico, lluvia,
                      pasajeros, t_base, round(max(tiempo, 1), 2)])

    columnas = ["origen", "destino", "dia", "hora", "hora_pico", "lluvia",
                "pasajeros", "tiempo_base", "tiempo_real"]
    return pd.DataFrame(filas, columns=columnas)


df = generar_dataset(3000)
df.to_csv("dataset_transmilenio.csv", index=False)

# ---------------------------------------------------------------
# 3. EXPLORACIÓN DE LOS DATOS
# ---------------------------------------------------------------
print("=== Primeras filas ===")
print(df.head())
print("\n=== Estadísticas ===")
print(df.describe().round(2))
print("\nValores nulos:", df.isnull().sum().sum())

# Gráfica: tiempo real según hora pico
plt.figure(figsize=(6, 4))
df.boxplot(column="tiempo_real", by="hora_pico")
plt.title("Tiempo real de viaje según hora pico")
plt.suptitle("")
plt.xlabel("Hora pico (0 = No, 1 = Sí)")
plt.ylabel("Minutos")
plt.tight_layout()
plt.savefig("grafica_hora_pico.png", dpi=120)
plt.close()

# ---------------------------------------------------------------
# 4. PREPROCESAMIENTO Y DIVISIÓN ENTRENAMIENTO / PRUEBA
# ---------------------------------------------------------------
X = df.drop(columns="tiempo_real")   # variables de entrada
y = df["tiempo_real"]                # variable a predecir

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)
print(f"\nEntrenamiento: {len(X_train)} filas | Prueba: {len(X_test)} filas")

# Las columnas de texto se convierten a números con One-Hot Encoding
columnas_texto = ["origen", "destino", "dia"]
preprocesador = ColumnTransformer(
    [("cat", OneHotEncoder(handle_unknown="ignore"), columnas_texto)],
    remainder="passthrough")   # las columnas numéricas pasan sin cambios

# ---------------------------------------------------------------
# 5. ENTRENAMIENTO Y EVALUACIÓN DE DOS MODELOS
# ---------------------------------------------------------------
modelos = {
    "Regresión Lineal": LinearRegression(),
    "Random Forest": RandomForestRegressor(n_estimators=200, random_state=42),
}

entrenados = {}
resultados = []
for nombre, algoritmo in modelos.items():
    pipe = Pipeline([("prep", preprocesador), ("modelo", algoritmo)])
    pipe.fit(X_train, y_train)
    pred = pipe.predict(X_test)

    mae = mean_absolute_error(y_test, pred)
    rmse = np.sqrt(mean_squared_error(y_test, pred))
    r2 = r2_score(y_test, pred)
    resultados.append([nombre, round(mae, 3), round(rmse, 3), round(r2, 3)])
    entrenados[nombre] = (pipe, pred)

tabla = pd.DataFrame(resultados, columns=["Modelo", "MAE", "RMSE", "R2"])
print("\n=== Comparación de modelos ===")
print(tabla.to_string(index=False))

# Gráfica: valores reales vs predichos del mejor modelo
mejor = tabla.sort_values("R2", ascending=False).iloc[0]["Modelo"]
pipe_mejor, pred_mejor = entrenados[mejor]
plt.figure(figsize=(5, 5))
plt.scatter(y_test, pred_mejor, alpha=0.4)
lim = [y_test.min(), y_test.max()]
plt.plot(lim, lim, "r--")
plt.xlabel("Tiempo real (min)")
plt.ylabel("Tiempo predicho (min)")
plt.title(f"Real vs predicho - {mejor}")
plt.tight_layout()
plt.savefig("grafica_real_vs_predicho.png", dpi=120)
plt.close()

# ---------------------------------------------------------------
# 6. GUARDAR EL MEJOR MODELO Y PREDECIR UN CASO NUEVO
# ---------------------------------------------------------------
joblib.dump(pipe_mejor, "modelo_transmilenio.joblib")
print(f"\nMejor modelo: {mejor} (guardado en modelo_transmilenio.joblib)")

caso = pd.DataFrame([{
    "origen": "Calle 100", "destino": "Héroes", "dia": "Lunes",
    "hora": 7, "hora_pico": 1, "lluvia": 1, "pasajeros": 320, "tiempo_base": 5}])
estimado = pipe_mejor.predict(caso)[0]
print(f"Calle 100 -> Héroes (lunes 7am, lluvia, hora pico): "
      f"{estimado:.2f} min (tiempo base: 5 min)")
