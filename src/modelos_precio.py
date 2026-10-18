"""
Entrega 3 - Partes 3 y 4
Simulación del precio con el modelo diario y con el modelo lognormal anual.
"""
import numpy as np
import pandas as pd

Z_95 = 1.96


def modelo_diario(S0, mu, sigma, horizontes=(10, 20, 40), n_sim=10_000, seed=42):
    """
    dS = mu*S0*dt + sigma*S0*eps*sqrt(dt),  eps ~ N(0,1)
    mu y sigma DIARIOS, dt en DIAS.
    Regresa la tabla de resultados y los precios simulados por horizonte.
    """
    rng = np.random.default_rng(seed)
    filas, sims = [], {}
    for dt in horizontes:
        eps = rng.standard_normal(n_sim)
        S_T = S0 + mu * S0 * dt + sigma * S0 * eps * np.sqrt(dt)
        sims[dt] = S_T

        esperado = S0 * (1 + mu * dt)
        margen = Z_95 * sigma * S0 * np.sqrt(dt)
        filas.append({
            "horizonte_dias": dt,
            "E[S_T] teorico": esperado,
            "IC95 inf": esperado - margen,
            "IC95 sup": esperado + margen,
            "E[S_T] simulado": S_T.mean(),
            "IC95 inf sim": np.percentile(S_T, 2.5),
            "IC95 sup sim": np.percentile(S_T, 97.5),
        })
    return pd.DataFrame(filas).set_index("horizonte_dias"), sims


def modelo_lognormal(S0, mu, sigma, meses=(3, 6, 9, 12), n_sim=10_000, seed=42):
    """
    ln S_T = ln S0 + (mu - sigma^2/2)*T + sigma*eps*sqrt(T),  eps ~ N(0,1)
    mu y sigma ANUALES, T en AÑOS.
    """
    rng = np.random.default_rng(seed)
    filas, sims = [], {}
    for m in meses:
        T = m / 12
        eps = rng.standard_normal(n_sim)
        centro = np.log(S0) + (mu - 0.5 * sigma**2) * T
        S_T = np.exp(centro + sigma * eps * np.sqrt(T))
        sims[m] = S_T

        filas.append({
            "horizonte_meses": m,
            "T (anios)": T,
            "E[S_T] teorico": S0 * np.exp(mu * T),
            "IC95 inf": np.exp(centro - Z_95 * sigma * np.sqrt(T)),
            "IC95 sup": np.exp(centro + Z_95 * sigma * np.sqrt(T)),
            "E[S_T] simulado": S_T.mean(),
            "IC95 inf sim": np.percentile(S_T, 2.5),
            "IC95 sup sim": np.percentile(S_T, 97.5),
        })
    return pd.DataFrame(filas).set_index("horizonte_meses"), sims
