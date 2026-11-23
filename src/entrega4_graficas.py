"""
Entrega 4 - Gráficas
Cada función guarda la figura en ../graficas y la regresa para mostrarla en el notebook.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

AZUL = "#1f4e79"
GRIS = "#7f7f7f"
OTROS = ["#d9822b", "#2e7d32", "#8e44ad", "#c62828", "#00838f"]

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


def heatmap(corr, activo, carpeta=None):
    n = len(corr)
    fig, ax = plt.subplots(figsize=(8.5, 7))
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(n)); ax.set_yticks(range(n))
    ax.set_xticklabels(corr.columns, rotation=35, ha="right")
    ax.set_yticklabels(corr.index)
    for i in range(n):
        for j in range(n):
            v = corr.values[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=9.5,
                    color="white" if abs(v) > 0.6 else "#222222",
                    fontweight="bold" if activo in (corr.index[i], corr.columns[j]) and i != j else "normal")
    k = list(corr.index).index(activo)
    ax.add_patch(plt.Rectangle((-0.5, k - 0.5), n, 1, fill=False, ec="black", lw=1.5))
    for s in ax.spines.values():
        s.set_visible(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.03)
    cb.set_label("Correlación de Pearson (rendimientos diarios)")
    ax.set_title("Matriz de correlación de los rendimientos logarítmicos diarios")
    fig.tight_layout()
    _guardar(fig, "e4_heatmap_correlacion", carpeta)
    return fig


def acumulado_base100(precios, activo, top, mercado, carpeta=None):
    base = precios / precios.iloc[0] * 100
    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.plot(base.index, base[mercado], color=GRIS, lw=1.6, ls="--", label=mercado, zorder=2)
    for c, col in zip(top, OTROS):
        ax.plot(base.index, base[c], color=col, lw=1.2, alpha=0.9, label=c, zorder=2)
    ax.plot(base.index, base[activo], color=AZUL, lw=2.2, label=activo, zorder=3)
    ultimo = base.iloc[-1].sort_values()
    # posiciones de las etiquetas sin encimarse (separación mínima en escala log)
    pos, prev = {}, None
    for c in [x for x in ultimo.index if x in [mercado, activo] + list(top)]:
        y = ultimo[c] if prev is None else max(ultimo[c], prev * 1.09)
        pos[c], prev = y, y
    for c in [mercado] + list(top) + [activo]:
        color = AZUL if c == activo else (GRIS if c == mercado else OTROS[list(top).index(c)])
        ax.annotate(f"{c}: {ultimo[c]:,.0f}", xy=(base.index[-1], ultimo[c]), xytext=(base.index[-1] + pd.Timedelta(days=40), pos[c]),
                    textcoords="data", va="center", fontsize=8.5, color=color,
                    arrowprops=dict(arrowstyle="-", color=color, lw=0.6) if abs(pos[c] / ultimo[c] - 1) > 0.02 else None)
    ax.axhline(100, color="#bbbbbb", lw=0.8)
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.set_xlim(base.index[0], base.index[-1] + pd.Timedelta(days=420))
    ax.set_title(f"Rendimiento acumulado (base 100 = {base.index[0]:%d-%m-%Y}): {activo}, sus 3 activos más correlacionados y el {mercado}")
    ax.set_ylabel("Valor de 100 invertidos (escala log)")
    ax.grid(True, ls="--", alpha=0.4)
    ax.legend(loc="upper left", frameon=False)
    fig.tight_layout()
    _guardar(fig, "e4_rendimiento_acumulado", carpeta)
    return fig


def correlacion_movil(cm, activo, carpeta=None):
    fig, ax = plt.subplots(figsize=(13, 5))
    for c, col in zip(cm.columns, [GRIS] + OTROS):
        ax.plot(cm.index, cm[c], color=col, lw=1.4, label=f"{activo} vs {c}")
    ax.axhline(0, color="#bbbbbb", lw=0.8)
    ax.set_ylim(min(-0.1, cm.min().min() - 0.05), 1)
    ax.set_title(f"Correlación móvil de 1 año (252 días) de {activo}")
    ax.set_ylabel("Correlación de Pearson")
    ax.grid(True, ls="--", alpha=0.4)
    ax.legend(loc="upper left", frameon=False, ncol=len(cm.columns))
    fig.tight_layout()
    _guardar(fig, "e4_correlacion_movil", carpeta)
    return fig
