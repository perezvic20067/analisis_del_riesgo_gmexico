import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Descargar datos
ticker = "GMEXICOB.MX"
data = yf.download(ticker, start="2000-01-01")

# Aplanar el MultiIndex
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.droplevel(1)

# Precio
precio_col = 'Adj Close' if 'Adj Close' in data.columns else 'Close'

# 1. Rendimiento logarítmico diario
data['Retorno_Log'] = np.log(data[precio_col] / data[precio_col].shift(1))
data.dropna(inplace=True)

# Añadir columna de año para agrupar
data['Year'] = data.index.year

# 2. Agrupar por año y calcular rendimientos medios y volatilidad diarios
resumen_anual = data.groupby('Year')['Retorno_Log'].agg(['mean', 'std'])
resumen_anual.rename(columns={'mean': 'Rend_Diario', 'std': 'Volatilidad_Diaria'}, inplace=True)

# 3. Anualizar considerando 252 días
resumen_anual['Rendimiento_Anualizado'] = resumen_anual['Rend_Diario'] * 252
resumen_anual['Volatilidad_Anualizada'] = resumen_anual['Volatilidad_Diaria'] * np.sqrt(252)

# Mostrar la tabla anualizada
print(resumen_anual[['Rendimiento_Anualizado', 'Volatilidad_Anualizada']])

# 4. Gráficas
fig, ax = plt.subplots(2, 1, figsize=(14, 10))
resumen_anual['Rendimiento_Anualizado'].plot(kind='bar', ax=ax[0], color='royalblue', edgecolor='black')
ax[0].set_title('Rendimiento Medio Anualizado (GMEXICOB.MX)')
ax[0].set_ylabel('Rendimiento')

resumen_anual['Volatilidad_Anualizada'].plot(kind='bar', ax=ax[1], color='crimson', edgecolor='black')
ax[1].set_title('Volatilidad Anualizada (GMEXICOB.MX)')
ax[1].set_ylabel('Volatilidad')

plt.tight_layout()

ruta_grafica = os.path.join('..', 'graficas', 'rendimiento_y_volatilidad_anual.png')

plt.savefig(ruta_grafica, dpi=300, bbox_inches='tight')