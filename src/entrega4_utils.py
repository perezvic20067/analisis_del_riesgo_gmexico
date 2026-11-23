"""
Entrega 4 - Correlación con el mercado y otros activos
Limpieza, rendimientos, correlaciones, beta y diversificación.
"""
import numpy as np
import pandas as pd

DIAS = 252


def limpiar(precios):
    """Conserva solo los días en que todos los activos tienen precio."""
    return precios.dropna(how="any").sort_index()


def rend_log(precios):
    """r_t = ln(S_t / S_{t-1})"""
    return np.log(precios / precios.shift(1)).dropna(how="any")


def resumen_observaciones(precios_brutos, precios_limpios, rend):
    filas = []
    for c in precios_brutos.columns:
        s = precios_brutos[c].dropna()
        filas.append({"Activo": c, "Días con precio": len(s),
                      "Primer dato": s.index.min().date(), "Último dato": s.index.max().date()})
    tabla = pd.DataFrame(filas)
    info = {
        "dias_comunes": len(precios_limpios),
        "rendimientos": len(rend),
        "inicio": rend.index.min().date(),
        "fin": rend.index.max().date(),
    }
    return tabla, info


def estadisticas(rend):
    """Media y volatilidad anualizadas de los rendimientos logarítmicos."""
    return pd.DataFrame({
        "Rend. medio anual": rend.mean() * DIAS * 100,
        "Volatilidad anual": rend.std() * np.sqrt(DIAS) * 100,
    })


def ranking(corr, activo):
    """Correlación del activo con cada uno de los demás, de mayor a menor."""
    r = corr[activo].drop(activo).sort_values(ascending=False)
    return pd.DataFrame({"Activo": r.index, "Correlación": r.values, "Lugar": range(1, len(r) + 1)})


def corr_precios_vs_rend(precios, rend, activo):
    """Compara la correlación medida en precios contra la medida en rendimientos."""
    cp = precios.corr()[activo].drop(activo)
    cr = rend.corr()[activo].drop(activo)
    return pd.DataFrame({"Activo": cp.index, "En precios": cp.values, "En rendimientos": cr.loc[cp.index].values})


def beta(rend, activo, mercado):
    cov = rend[[activo, mercado]].cov().iloc[0, 1]
    b = cov / rend[mercado].var()
    r2 = rend[activo].corr(rend[mercado]) ** 2
    return b, r2


def desempeno(precios):
    """Rendimiento total, anual compuesto, volatilidad y caída máxima por activo."""
    anios = (precios.index[-1] - precios.index[0]).days / 365.25
    filas = []
    for c in precios.columns:
        s = precios[c]
        total = s.iloc[-1] / s.iloc[0] - 1
        cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / anios) - 1
        vol = np.log(s / s.shift(1)).std() * np.sqrt(DIAS)
        caida = (s / s.cummax() - 1).min()
        filas.append({"Activo": c, "Base 100 al final": 100 * (1 + total), "Rend. total": total * 100,
                      "Rend. anual compuesto": cagr * 100, "Volatilidad anual": vol * 100,
                      "Caída máxima": caida * 100})
    return pd.DataFrame(filas)


def corr_movil(rend, activo, otros, ventana=DIAS):
    return pd.DataFrame({o: rend[activo].rolling(ventana).corr(rend[o]) for o in otros}).dropna(how="all")


def diversificacion(rend, activo):
    """Volatilidad de un portafolio 50/50 del activo con cada uno de los demás."""
    vol_a = rend[activo].std() * np.sqrt(DIAS)
    filas = []
    for o in rend.columns.drop(activo):
        port = 0.5 * rend[activo] + 0.5 * rend[o]
        vol_o = rend[o].std() * np.sqrt(DIAS)
        vol_p = port.std() * np.sqrt(DIAS)
        promedio = 0.5 * vol_a + 0.5 * vol_o
        filas.append({"Activo": o, "Correlación": rend[activo].corr(rend[o]),
                      "Vol. del otro activo": vol_o * 100, "Vol. 50/50": vol_p * 100,
                      "Reducción vs promedio": (1 - vol_p / promedio) * 100})
    return pd.DataFrame(filas).sort_values("Correlación"), vol_a * 100
