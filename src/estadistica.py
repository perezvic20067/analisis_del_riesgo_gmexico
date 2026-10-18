"""
Entrega 3 - Partes 1 y 2
Rendimiento y volatilidad por año, pruebas de normalidad y prueba de hipótesis
sobre el rendimiento promedio.
"""
import numpy as np
import pandas as pd
from scipy import stats

DIAS_HABILES = 252


def resumen_anual(df, col="log_return", dias=DIAS_HABILES):
    """Rendimiento medio y volatilidad por año, en escala diaria y anualizada."""
    g = df.groupby(df.index.year)[col]
    tabla = pd.DataFrame({
        "dias": g.count(),
        "mu_diario": g.mean(),
        "sigma_diaria": g.std(),
    })
    tabla["mu_anual"] = tabla["mu_diario"] * dias
    tabla["sigma_anual"] = tabla["sigma_diaria"] * np.sqrt(dias)
    # Equivalente en rendimiento simple: e^mu - 1
    tabla["rend_simple_equiv"] = np.exp(tabla["mu_anual"]) - 1
    tabla.index.name = "anio"
    return tabla


def parametros_historicos(serie, dias=DIAS_HABILES):
    """mu y sigma de todo el historial, diarios y anuales."""
    mu_d, sigma_d = serie.mean(), serie.std()
    return {
        "mu_diario": mu_d,
        "sigma_diaria": sigma_d,
        "mu_anual": mu_d * dias,
        "sigma_anual": sigma_d * np.sqrt(dias),
    }


def prueba_normalidad(serie, nombre, alpha=0.05):
    """Jarque-Bera: sesgo, curtosis (no en exceso), estadístico, valor p y conclusión."""
    x = serie.dropna()
    jb, p = stats.jarque_bera(x)
    return {
        "variable": nombre,
        "n": len(x),
        "sesgo": stats.skew(x),
        "curtosis": stats.kurtosis(x, fisher=False),  # normal = 3
        "JB": jb,
        "valor_p": p,
        "conclusion": "Se rechaza H0: no es normal" if p < alpha else "No se rechaza H0: normal",
    }


def prueba_media_cero(serie, alpha=0.05):
    """Prueba t de dos colas. H0: mu = 0  vs  H1: mu != 0."""
    x = serie.dropna()
    n, media, s = len(x), x.mean(), x.std()
    t, p = stats.ttest_1samp(x, 0)
    return {
        "n": n,
        "media": media,
        "desv_est": s,
        "error_est": s / np.sqrt(n),
        "t": t,
        "valor_p": p,
        "t_critico": stats.t.ppf(1 - alpha / 2, n - 1),
        "conclusion": "Se rechaza H0: mu distinto de 0" if p < alpha else "No se rechaza H0: mu = 0",
    }


def dias_extremos(serie, k=3):
    """Compara % de días con |r - media| > k*sigma contra lo que predice una normal."""
    x = serie.dropna()
    z = (x - x.mean()) / x.std()
    observado = (z.abs() > k).mean()
    esperado = 2 * (1 - stats.norm.cdf(k))
    return {"k": k, "n_dias": int((z.abs() > k).sum()), "observado": observado,
            "esperado": esperado, "veces_mas": observado / esperado}
