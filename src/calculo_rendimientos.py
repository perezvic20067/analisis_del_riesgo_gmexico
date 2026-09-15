import pandas as pd
import numpy as np
import os


def calculate_returns(filepath):

    # Carga el CSV estableciendo la fecha como el indice de la tabla
    df = pd.read_csv(filepath, index_col='Date', parse_dates=True)

    # 1. Rendimiento Simple: (Precio de hoy - Precio de ayer) / Precio de ayer
    df['simple_return'] = df['adj_close'].pct_change()

    # 2. Rendimiento Logaritmico Continuo: ln(Precio de hoy / Precio de ayer)
    df['log_return'] = np.log(df['adj_close'] / df['adj_close'].shift(1))

    # 3. Rendimiento Acumulado: Muestra la evolucion de $1 invertido desde el inicio
    df['cumulative_return'] = (1 + df['simple_return']).cumprod()

    # Elimina el primer registro porque no hay un "dia anterior" contra el cual comparar
    df = df.dropna()

    return df


if __name__ == "__main__":
    # Construye la ruta hacia los CSVs que descargamos en el script anterior
    gmexico_path = os.path.join("..", "datos_historicos", "gmexico_prices.csv")
    ipc_path = os.path.join("..", "datos_historicos", "ipc_prices.csv")

    # Calculos para Grupo Mexico y para el IPC
    df_gmexico = calculate_returns(gmexico_path)
    df_ipc = calculate_returns(ipc_path)

    print("\nRendimientos de los ultimos 5 días:")
    # Imprimimos los ultimos 5 dias (tail) para ver el rendimiento acumulado mas reciente
    print(df_gmexico[['adj_close', 'simple_return', 'log_return', 'cumulative_return']].tail())