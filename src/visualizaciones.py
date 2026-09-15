import matplotlib.pyplot as plt
import os
import pandas as pd
from calculo_rendimientos import calculate_returns


def plot_price_evolution_with_intervals(df, ticker, filename):

    fig, ax = plt.subplots(figsize=(14, 7))

    # 1. Dibujamos la linea base
    ax.plot(df.index, df['adj_close'], label=f'{ticker} (Precio Ajustado)', color='#1f77b4', linewidth=1.5)

    # Intervalos o cambios en tendencias
    intervalos = [
        {
            'inicio': '2008-06-01', 'fin': '2008-11-30',
            'color': 'red', 'texto': 'Crisis Subprime\n(Colapso Cobre)'
        },
        {
            'inicio': '2020-03-01', 'fin': '2021-05-01',
            'color': 'green', 'texto': 'Rebote Post-COVID\n(Estimulos)'
        },
        {
            'inicio': '2023-01-01', 'fin': '2026-08-01',
            'color': 'green', 'texto': 'Rally Secular\n(Nearshoring/VE)'
        }
    ]

    y_max = df['adj_close'].max()

    for intervalo in intervalos:
        fecha_ini = pd.to_datetime(intervalo['inicio'])
        fecha_fin = pd.to_datetime(intervalo['fin'])

        # Sombreado del fondo
        ax.axvspan(fecha_ini, fecha_fin, color=intervalo['color'], alpha=0.15, zorder=1)

        # Etiqueta de texto (centrada en el intervalo)
        fecha_media = fecha_ini + (fecha_fin - fecha_ini) / 2
        ax.text(fecha_media, y_max * 0.95, intervalo['texto'],
                color=intervalo['color'], fontsize=9, fontweight='bold', ha='center', va='top',
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=intervalo['color'], lw=1, alpha=0.8))

    ax.set_title(f'Evolucion Historica y Ciclos Macroeconomicos - {ticker}', fontsize=14, fontweight='bold')
    ax.set_xlabel('Fecha', fontsize=10)
    ax.set_ylabel('Precio (MXN)', fontsize=10)
    ax.legend(loc='upper left')
    ax.grid(True, linestyle='--', alpha=0.6)

    save_path = os.path.join("..", "graficas", f"{filename}.png")
    plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.show()


def plot_cumulative_comparison(df_asset, df_benchmark, filename):

    plt.figure(figsize=(12, 6))
    plt.plot(df_asset.index, df_asset['cumulative_return'], label='Grupo Mexico', color='blue', linewidth=1.5)
    plt.plot(df_benchmark.index, df_benchmark['cumulative_return'], label='IPC (Benchmark)', color='orange',
             linewidth=1.5)

    plt.title('Comparacion de Rendimiento Acumulado: GMEXICOB vs IPC', fontsize=14, fontweight='bold')
    plt.xlabel('Fecha', fontsize=10)
    plt.ylabel('Multiplicador de Inversion (Base 1)', fontsize=10)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)

    save_path = os.path.join("..", "graficas", f"{filename}.png")
    plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.show()

if __name__ == "__main__":
    gmexico_path = os.path.join("..", "datos_historicos", "gmexico_prices.csv")
    ipc_path = os.path.join("..", "datos_historicos", "ipc_prices.csv")

    # Calculamos los rendimientos
    df_gmexico = calculate_returns(gmexico_path)
    df_ipc = calculate_returns(ipc_path)

    # Gráfica 1 con los cambios en tendencias
    plot_price_evolution_with_intervals(df_gmexico, "GMEXICOB", "evolucion_precio_intervalos")

    # Gráfica 2 con comparación con el IPC
    df_gmexico_aligned, df_ipc_aligned = df_gmexico.align(df_ipc, join='inner', axis=0)

    # Recalculamos
    df_gmexico_aligned['cumulative_return'] = (1 + df_gmexico_aligned['simple_return']).cumprod()
    df_ipc_aligned['cumulative_return'] = (1 + df_ipc_aligned['simple_return']).cumprod()

    # Generamos la segunda gráfica
    plot_cumulative_comparison(df_gmexico_aligned, df_ipc_aligned, "comparacion_acumulada_ipc")