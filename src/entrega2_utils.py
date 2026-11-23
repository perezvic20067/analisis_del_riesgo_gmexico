"""
Entrega 2 - Cálculos de apoyo
Resumen de rendimientos, inversión inicial, periodos, relación con el PIB,
tabla trimestral y reacción del precio a eventos.
"""
import numpy as np
import pandas as pd


# ---------------------------------------------------------------- Parte 1

def resumen_rendimientos(df_precios, df_rend, dias=252):
    """Compara rendimiento simple, logarítmico y acumulado de toda la historia."""
    p0, p1 = df_precios["adj_close"].iloc[0], df_precios["adj_close"].iloc[-1]
    anios = (df_precios.index[-1] - df_precios.index[0]).days / 365.25
    multiplicador = p1 / p0
    return pd.DataFrame({
        "Medida": [
            "Rendimiento simple diario promedio",
            "Rendimiento logarítmico diario promedio",
            "Volatilidad diaria (desv. est. del rend. log.)",
            "Rendimiento logarítmico anualizado (×252)",
            "Rendimiento acumulado total",
            "Rendimiento anual compuesto (CAGR)",
        ],
        "Valor": [
            f"{df_rend['simple_return'].mean():.4%}",
            f"{df_rend['log_return'].mean():.4%}",
            f"{df_rend['log_return'].std():.4%}",
            f"{df_rend['log_return'].mean() * dias:.2%}",
            f"{multiplicador - 1:,.0%}",
            f"{multiplicador ** (1 / anios) - 1:.2%}",
        ],
    })


def inversion_inicial(df_precios, monto=10_000):
    """Valor final de un monto invertido en el primer precio disponible."""
    p0, p1 = df_precios["adj_close"].iloc[0], df_precios["adj_close"].iloc[-1]
    return {
        "fecha_inicio": df_precios.index[0].date(),
        "fecha_fin": df_precios.index[-1].date(),
        "monto": monto,
        "valor_final": monto * p1 / p0,
        "multiplicador": p1 / p0,
    }


def precio_en(df, fecha):
    """Último precio disponible en o antes de la fecha."""
    sub = df.loc[:pd.to_datetime(fecha)]
    if sub.empty:
        return df.iloc[0]["adj_close"], df.index[0]
    return sub.iloc[-1]["adj_close"], sub.index[-1]


def tabla_periodos(df, periodos):
    filas = []
    for k, p in enumerate(periodos, start=1):
        p0, d0 = precio_en(df, p["inicio"])
        p1, d1 = precio_en(df, p["fin"])
        dias = (d1 - d0).days
        filas.append({
            "#": k,
            "Inicio": d0.date(),
            "Fin": d1.date(),
            "Precio inicio (MXN)": round(p0, 2),
            "Precio fin (MXN)": round(p1, 2),
            "Magnitud (%)": round((p1 / p0 - 1) * 100, 1),
            "Duración (meses)": round(dias / 30.44, 1),
            "Patrón visual": p["patron"],
        })
    return pd.DataFrame(filas)


# ---------------------------------------------------------------- Parte 2

def retornos_anuales(df):
    """Retorno anual (%) con el último precio de cada año."""
    cierre = df["adj_close"].resample("YE").last()
    ret = cierre.pct_change() * 100
    ret.index = ret.index.year
    return ret


def correlaciones_desfase(datos, col_activo="retorno_gmexico", col_pib="pib_crecimiento"):
    """
    Correlación de Pearson entre el retorno del activo y el PIB con desfases:
    PIB del año anterior (activo rezagado), mismo año (coincidente) y año siguiente (activo adelantado).
    """
    x = datos[col_activo]
    filas = []
    for desfase, etiqueta in [(1, "PIB del año anterior → activo rezagado"),
                              (0, "PIB del mismo año → activo coincidente"),
                              (-1, "PIB del año siguiente → activo adelantado")]:
        y = datos[col_pib].shift(desfase)
        par = pd.concat([x, y], axis=1).dropna()
        filas.append({"Comparación": etiqueta,
                      "Correlación (R)": round(par.iloc[:, 0].corr(par.iloc[:, 1]), 3),
                      "Años": len(par)})
    return pd.DataFrame(filas)


def divergencias(datos, n=6, col_activo="retorno_gmexico", col_pib="pib_crecimiento"):
    """Años donde el activo y el PIB se movieron en sentido contrario, ordenados por la brecha."""
    d = datos.copy()
    d["mismo_signo"] = np.sign(d[col_activo]) == np.sign(d[col_pib])
    d["brecha"] = (d[col_activo] - d[col_pib]).abs()
    out = d[~d["mismo_signo"]].sort_values("brecha", ascending=False).head(n)
    return out[[col_activo, col_pib]].round(1)


# ---------------------------------------------------------------- Parte 3

def tabla_trimestral(datos, acciones):
    """
    datos: dict trimestre -> {ventas, ebitda, utilidad} en millones de USD (orden cronológico).
    Devuelve márgenes, EPS y variaciones QoQ / YoY.
    """
    df = pd.DataFrame(datos).T.astype(float)
    df["margen_ebitda"] = df["ebitda"] / df["ventas"] * 100
    df["margen_neto"] = df["utilidad"] / df["ventas"] * 100
    df["eps"] = df["utilidad"] * 1e6 / acciones
    for col in ["ventas", "ebitda", "utilidad", "eps"]:
        df[f"{col}_qoq"] = df[col].pct_change(1, fill_method=None) * 100
        df[f"{col}_yoy"] = df[col].pct_change(4, fill_method=None) * 100
    return df


def _cambio(df, fecha, d):
    """Cambio % de d días hábiles (el día del evento cuenta como el día 1) contra el cierre previo."""
    antes = df.loc[:fecha - pd.Timedelta(days=1)]
    despues = df.loc[fecha:]
    if antes.empty or len(despues) < d:
        return np.nan, antes.iloc[-1]["adj_close"] if not antes.empty else np.nan
    base = antes.iloc[-1]["adj_close"]
    return (despues.iloc[d - 1]["adj_close"] / base - 1) * 100, base


def reaccion_eventos(df, eventos, dias=(1, 5, 10), df_ref=None, dias_ref=5):
    """
    Cambio % del precio después de cada evento.
    Base: cierre del día hábil anterior al evento. d = días hábiles después.
    Si se da df_ref (IPC), agrega la reacción a dias_ref días menos la del IPC.
    """
    filas = []
    for k, ev in enumerate(eventos, start=1):
        fecha = pd.to_datetime(ev["fecha"])
        _, base = _cambio(df, fecha, 1)
        fila = {"#": k, "Fecha": fecha.date(), "Evento": ev["descripcion"],
                "Precio previo (MXN)": round(base, 2)}
        for d in dias:
            r, _ = _cambio(df, fecha, d)
            fila[f"{d} día{'s' if d > 1 else ''}"] = round(r, 1) if not np.isnan(r) else np.nan
        if df_ref is not None:
            r_a, _ = _cambio(df, fecha, dias_ref)
            r_b, _ = _cambio(df_ref, fecha, dias_ref)
            fila[f"{dias_ref} días vs IPC"] = round(r_a - r_b, 1) if not np.isnan(r_a - r_b) else np.nan
        filas.append(fila)
    return pd.DataFrame(filas)
