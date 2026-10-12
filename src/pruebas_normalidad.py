import os
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import jarque_bera, skew, kurtosis, norm

# Datos
ticker = "GMEXICOB.MX"
data = yf.download(ticker, start="2000-01-01")

# Aplanar el MultiIndex
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.droplevel(1)

# Precio
precio_col = 'Adj Close' if 'Adj Close' in data.columns else 'Close'

# Calcular el rendimiento logarítmico
data['Retorno_Log'] = np.log(data[precio_col] / data[precio_col].shift(1))
data.dropna(inplace=True)


# 2. Prueba Normalidad
def aplicar_prueba_normalidad(serie, nombre_variable):
    s = skew(serie.dropna())
    k = kurtosis(serie.dropna()) + 3
    jb_stat, p_value = jarque_bera(serie.dropna())

    print(f"--- Resultados para: {nombre_variable} ---")
    print(f"Sesgo (S): {s:.4f}")
    print(f"Curtosis (K): {k:.4f}")
    print(f"Estadístico JB: {jb_stat:.4f}")
    print(f"Valor p: {p_value:.6f}")

    if p_value < 0.05:
        print("Conclusión: Se rechaza la hipótesis nula. La variable NO se distribuye de forma normal.\n")
    else:
        print("Conclusión: No se rechaza la hipótesis nula. La variable se distribuye de forma normal.\n")


# 3. Prueba
aplicar_prueba_normalidad(data['Retorno_Log'], 'Rendimiento Logarítmico Diario')
aplicar_prueba_normalidad(data[precio_col], 'Precio del Activo')

# 4. Graficas
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Histograma de rendimientos
sns.histplot(data['Retorno_Log'].dropna(), bins=100, stat="density", ax=axes[0], color='skyblue', edgecolor=None)
x_rend = np.linspace(data['Retorno_Log'].min(), data['Retorno_Log'].max(), 100)
p_rend = norm.pdf(x_rend, data['Retorno_Log'].mean(), data['Retorno_Log'].std())
axes[0].plot(x_rend, p_rend, 'k--', linewidth=2, label='Curva Normal Teórica')
axes[0].set_title('Distribución: Rendimiento Logarítmico')
axes[0].legend()

# Histograma para el precio
sns.histplot(data[precio_col].dropna(), bins=100, stat="density", ax=axes[1], color='lightgreen', edgecolor=None)
x_precio = np.linspace(data[precio_col].min(), data[precio_col].max(), 100)
p_precio = norm.pdf(x_precio, data[precio_col].mean(), data[precio_col].std())
axes[1].plot(x_precio, p_precio, 'k--', linewidth=2, label='Curva Normal Teórica')
axes[1].set_title('Distribución: Precio del Activo')
axes[1].legend()

plt.tight_layout()

# 5. Guardar gráfica en carpeta
ruta_grafica = os.path.join('..', 'graficas', 'histogramas_normalidad.png')
plt.savefig(ruta_grafica, dpi=300, bbox_inches='tight')
print(f"Gráfica guardada exitosamente en: {ruta_grafica}")

plt.show()