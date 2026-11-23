"""
Entrega 2 - Gráficas
Todas las funciones dibujan la figura, la guardan en ../graficas y la regresan
para que el notebook la muestre (y quede incrustada en el HTML).
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

AZUL = "#1f4e79"
NARANJA = "#d9822b"
GRIS = "#8c8c8c"
VERDE = "#2e7d32"
ROJO = "#c62828"
COLOR_TIPO = {"alza": "#c8e6c9", "caida": "#ffcdd2", "lateral": "#e0e0e0"}

plt.rcParams.update({
    "figure.dpi": 110,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titleweight": "bold",
    "axes.titlesize": 13,
    "axes.titlelocation": "left",
    "font.size": 10,
})


def _guardar(fig, nombre, carpeta):
    if carpeta:
        fig.savefig(os.path.join(carpeta, f"{nombre}.png"), dpi=200, bbox_inches="tight")


def _formato_mxn(ax):
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}" if v >= 1 else f"${v:.1f}"))


def precio_con_periodos(df, tabla_periodos, tipos, eventos, carpeta=None):
    """Precio histórico en escala log, con los periodos de la tabla sombreados y eventos clave."""
    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.plot(df.index, df["adj_close"], color=AZUL, lw=1.2, zorder=3)
    ax.set_yscale("log")
    _formato_mxn(ax)

    y_top = df["adj_close"].max() * 1.7
    for (_, fila), tipo in zip(tabla_periodos.iterrows(), tipos):
        ini, fin = pd.to_datetime(fila["Inicio"]), pd.to_datetime(fila["Fin"])
        ax.axvspan(ini, fin, color=COLOR_TIPO[tipo], alpha=0.75, zorder=1, lw=0)
        ax.text(ini + (fin - ini) / 2, y_top, str(fila["#"]), ha="center", va="top",
                fontsize=10, fontweight="bold", color="#333333")

    for ev in eventos:
        f = pd.to_datetime(ev["fecha"])
        precio = df.loc[:f, "adj_close"].iloc[-1]
        ax.annotate(ev["texto"], xy=(f, precio), xytext=ev.get("offset", (0, 40)),
                    textcoords="offset points", ha="center", fontsize=8.5,
                    arrowprops=dict(arrowstyle="-", color="#555555", lw=0.8),
                    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#999999", lw=0.6), zorder=5)

    ax.set_ylim(df["adj_close"].min() * 0.6, y_top * 1.05)
    ax.set_xlim(df.index[0] - pd.Timedelta(days=60), df.index[-1] + pd.Timedelta(days=60))
    ax.set_title("GMEXICOB: precio ajustado diario y los 10 periodos significativos (escala logarítmica)")
    ax.set_ylabel("Precio ajustado (MXN, escala log)")
    ax.grid(True, which="major", ls="--", alpha=0.4)
    ax.legend(handles=[Patch(color=COLOR_TIPO["alza"], label="Alza"),
                       Patch(color=COLOR_TIPO["caida"], label="Caída"),
                       Patch(color=COLOR_TIPO["lateral"], label="Consolidación / lateral")],
              loc="lower right", frameon=False, ncol=3)
    fig.tight_layout()
    _guardar(fig, "evolucion_precio_intervalos", carpeta)
    return fig


def acumulado_vs_ipc(df_activo, df_ipc, monto=10_000, carpeta=None):
    """Valor de una inversión inicial en GMEXICOB vs el IPC (escala log)."""
    a = monto * df_activo["cumulative_return"]
    b = monto * df_ipc["cumulative_return"]
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(a.index, a, color=AZUL, lw=1.4, label="GMEXICOB")
    ax.plot(b.index, b, color=NARANJA, lw=1.4, label="IPC (S&P/BMV)")
    ax.set_yscale("log")
    _formato_mxn(ax)
    for serie, color in [(a, AZUL), (b, NARANJA)]:
        ax.annotate(f"${serie.iloc[-1]:,.0f}\n({serie.iloc[-1] / monto:,.1f} veces)",
                    xy=(serie.index[-1], serie.iloc[-1]), xytext=(8, 0), textcoords="offset points",
                    va="center", fontsize=9, color=color, fontweight="bold")
    ax.axhline(monto, color=GRIS, lw=0.8, ls=":")
    ax.set_title(f"Valor de ${monto:,.0f} MXN invertidos el {a.index[0]:%d-%m-%Y}: GMEXICOB vs IPC")
    ax.set_ylabel("Valor de la inversión (MXN, escala log)")
    ax.grid(True, ls="--", alpha=0.4)
    ax.legend(loc="upper left", frameon=False)
    ax.set_xlim(a.index[0], a.index[-1] + pd.Timedelta(days=1100))
    fig.tight_layout()
    _guardar(fig, "comparacion_acumulada_ipc", carpeta)
    return fig


def activo_vs_pib(base100, pib, carpeta=None):
    """Eje izquierdo: rendimiento acumulado base 100 (log). Eje derecho: crecimiento anual del PIB."""
    fig, ax1 = plt.subplots(figsize=(13, 6))
    ax2 = ax1.twinx()
    colores = [VERDE if v >= 0 else ROJO for v in pib.values]
    ax2.bar(pib.index, pib.values, color=colores, alpha=0.35, width=0.7, zorder=1)
    ax2.axhline(0, color=GRIS, lw=0.8)
    ax2.set_ylabel("Crecimiento anual del PIB de México (%)")
    ax2.spines["right"].set_visible(True)
    lim = max(abs(pib.min()), abs(pib.max())) * 1.3
    ax2.set_ylim(-lim, lim)

    ax1.set_zorder(ax2.get_zorder() + 1)
    ax1.patch.set_visible(False)
    ax1.plot(base100.index, base100.values, color=AZUL, lw=2, marker="o", ms=4)
    ax1.set_yscale("log")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax1.set_ylabel("GMEXICOB, rendimiento acumulado (base 100 = 2000, escala log)", color=AZUL)
    ax1.grid(True, ls="--", alpha=0.4)
    for anio in [2008, 2009, 2020]:
        if anio in pib.index:
            ax2.annotate(f"PIB {pib[anio]:+.1f}%", xy=(anio, pib[anio]), xytext=(0, -14 if pib[anio] < 0 else 6),
                         textcoords="offset points", ha="center", fontsize=8, color=ROJO)
    ax1.set_title("GMEXICOB (base 100) vs crecimiento anual del PIB de México")
    ax1.legend(handles=[Line2D([0], [0], color=AZUL, lw=2, marker="o", label="GMEXICOB base 100 (eje izq.)"),
                        Patch(color=VERDE, alpha=0.35, label="PIB % anual (eje der.)")],
               loc="upper left", frameon=False)
    fig.tight_layout()
    _guardar(fig, "gmexico_vs_pib", carpeta)
    return fig


def scatter_pib(datos, carpeta=None, anios_etiqueta=(2001, 2003, 2008, 2009, 2018, 2020, 2025)):
    from scipy import stats
    x, y = datos["pib_crecimiento"], datos["retorno_gmexico"]
    reg = stats.linregress(x, y)
    fig, ax = plt.subplots(figsize=(9.5, 6.5))
    ax.scatter(x, y, color=AZUL, s=55, alpha=0.85, edgecolor="white", zorder=3)
    xs = np.linspace(x.min() - 0.5, x.max() + 0.5, 50)
    ax.plot(xs, reg.slope * xs + reg.intercept, color=ROJO, lw=2, label="Línea de tendencia (MCO)")
    for anio in anios_etiqueta:
        if anio in datos.index:
            ax.annotate(str(anio), (x[anio], y[anio]), xytext=(5, 4), textcoords="offset points", fontsize=8.5)
    ax.axhline(0, color=GRIS, lw=0.8)
    ax.axvline(0, color=GRIS, lw=0.8)
    signo = "+" if reg.intercept >= 0 else "−"
    ax.text(0.98, 0.97,
            f"y = {reg.slope:.2f}x {signo} {abs(reg.intercept):.2f}\n"
            f"R (Pearson) = {reg.rvalue:.3f}\nR² = {reg.rvalue ** 2:.3f}\n"
            f"valor p = {reg.pvalue:.3f}\nn = {len(datos)} años ({datos.index.min()}–{datos.index.max()})",
            transform=ax.transAxes, va="top", ha="right", fontsize=10,
            bbox=dict(boxstyle="round", fc="white", ec="#999999"))
    ax.set_ylim(y.min() - 25, y.max() + 30)
    ax.set_title("Retorno anual de GMEXICOB vs crecimiento anual del PIB")
    ax.set_xlabel("Crecimiento anual del PIB de México (%)")
    ax.set_ylabel("Retorno anual de GMEXICOB (%)")
    ax.grid(True, ls="--", alpha=0.4)
    ax.legend(loc="lower right", frameon=False)
    fig.tight_layout()
    _guardar(fig, "scatter_gmexico_pib", carpeta)
    return fig, reg


def ultimos_12m(df, tabla_eventos, col_reaccion="5 días", carpeta=None):
    """Precio de los últimos 12 meses con eventos numerados y su reacción."""
    fin = df.index.max()
    sub = df.loc[fin - pd.Timedelta(days=365):]
    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.plot(sub.index, sub["adj_close"], color=AZUL, lw=1.5, zorder=3)
    _formato_mxn(ax)
    ymin, ymax = sub["adj_close"].min(), sub["adj_close"].max()
    ax.set_ylim(ymin * 0.88, ymax * 1.12)
    for i, (_, ev) in enumerate(tabla_eventos.iterrows()):
        f = pd.to_datetime(ev["Fecha"])
        precio = sub.loc[:f, "adj_close"].iloc[-1]
        r = ev[col_reaccion]
        txt = "n.d." if pd.isna(r) else f"{r:+.1f}%"
        color = GRIS if pd.isna(r) else (VERDE if r >= 0 else ROJO)
        arriba = i % 2 == 0
        ax.axvline(f, color=color, ls="--", lw=0.8, alpha=0.6, zorder=2)
        ax.annotate(f"{ev['#']}\n{txt}", xy=(f, precio), xytext=(0, 34 if arriba else -40),
                    textcoords="offset points", ha="center", fontsize=9, fontweight="bold", color=color,
                    arrowprops=dict(arrowstyle="-", color=color, lw=0.8),
                    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=color, lw=0.8), zorder=5)
    ax.set_title(f"GMEXICOB, últimos 12 meses: eventos clave y reacción del precio a {col_reaccion} hábiles")
    ax.set_ylabel("Precio ajustado (MXN)")
    ax.grid(True, ls="--", alpha=0.4)
    ax.text(0.0, -0.1, "Número = evento de la tabla. Porcentaje = cambio del precio contra el cierre previo al evento.",
            transform=ax.transAxes, fontsize=8.5, color="#555555")
    fig.tight_layout()
    _guardar(fig, "ultimos_12m_eventos", carpeta)
    return fig
