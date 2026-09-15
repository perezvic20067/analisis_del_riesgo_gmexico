import pandas as pd
import os
from calculo_rendimientos import calculate_returns


def identify_daily_shocks(df, threshold=0.15):  # Cambios drasticos en el precio de +-15%

    # Compara exactamente contra el dia anterior
    df['daily_return'] = df['adj_close'].pct_change(1)

    # Filtramos los eventos extremos
    shocks = df[abs(df['daily_return']) >= threshold].copy()
    shocks = shocks.sort_values(by='daily_return', ascending=False)

    return shocks


if __name__ == "__main__":
    # Cargamos los datos de Grupo Mexico
    gmexico_path = os.path.join("..", "datos_historicos", "gmexico_prices.csv")
    df_gmexico = calculate_returns(gmexico_path)

    # Deteccion de shocks
    shocks_diarios = identify_daily_shocks(df_gmexico, threshold=0.15)

    # Resultados separados por subidas y bajadas
    print("\n--- PRINCIPALES SALTOS DIARIOS (>15%) ---")
    print(shocks_diarios[shocks_diarios['daily_return'] > 0][['adj_close', 'daily_return']])

    print("\n--- PRINCIPALES CAIDAS DIARIAS (<-15%) ---")
    print(shocks_diarios[shocks_diarios['daily_return'] < 0][['adj_close', 'daily_return']])