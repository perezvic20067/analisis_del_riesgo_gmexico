"""
Entrega 4 - Descarga de precios
GMEXICOB, el IPC y 5 empresas mexicanas, del 1 de enero de 2016 a hoy.
Guarda ../datos_historicos/entrega4_precios.csv (una columna por activo, precio ajustado).

Uso (desde la carpeta src):  python descarga_entrega4.py
"""
import os
import pandas as pd
import yfinance as yf

INICIO = "2016-01-01"

# nombre en el reporte -> ticker de Yahoo Finance
ACTIVOS = {
    "GMEXICOB": "GMEXICOB.MX",
    "IPC": "^MXX",
    "PEÑOLES": "PE&OLES.MX",
    "CEMEX": "CEMEXCPO.MX",
    "ORBIA": "ORBIA.MX",
    "BANORTE": "GFNORTEO.MX",
    "AMÉRICA MÓVIL": "AMXB.MX",
}

# Si un ticker cambió de nombre y Yahoo no trae su historia completa,
# se completa con el ticker anterior (se re-escala en la primera fecha común).
RESPALDO = {
    "AMXB.MX": "AMXL.MX",     # América Móvil unificó sus series L y B en 2023
    "ORBIA.MX": "MEXCHEM.MX", # Mexichem cambió su nombre a Orbia en 2019
}


def bajar(ticker):
    h = yf.Ticker(ticker).history(start=INICIO, auto_adjust=True)
    if h.empty:
        return pd.Series(dtype=float, name=ticker)
    s = h["Close"].dropna()
    if s.index.tz is not None:
        s.index = s.index.tz_localize(None)
    s.index = s.index.normalize()
    return s


def bajar_con_respaldo(ticker):
    s = bajar(ticker)
    limite = pd.Timestamp(INICIO) + pd.Timedelta(days=30)
    if ticker in RESPALDO and (s.empty or s.index[0] > limite):
        viejo = bajar(RESPALDO[ticker])
        comunes = s.index.intersection(viejo.index)
        if not viejo.empty and len(comunes) > 0:
            f = comunes[0]
            viejo = viejo * s.loc[f] / viejo.loc[f]
            s = pd.concat([viejo.loc[:f - pd.Timedelta(days=1)], s])
            print(f"  {ticker}: historia completada con {RESPALDO[ticker]} antes del {f.date()}")
        elif not viejo.empty and s.empty:
            s = viejo
            print(f"  {ticker}: sin datos; se usó {RESPALDO[ticker]}")
    return s


if __name__ == "__main__":
    series = {}
    for nombre, ticker in ACTIVOS.items():
        s = bajar_con_respaldo(ticker)
        series[nombre] = s
        rango = f"{s.index[0].date()} a {s.index[-1].date()}" if not s.empty else "SIN DATOS"
        print(f"{nombre:15s} {ticker:12s} {len(s):5d} días  ({rango})")

    precios = pd.DataFrame(series)
    precios.index.name = "Date"
    ruta = os.path.join("..", "datos_historicos", "entrega4_precios.csv")
    precios.to_csv(ruta)

    completos = precios.dropna()
    print(f"\nGuardado en {ruta}")
    print(f"Días con precio de los 7 activos: {len(completos)} "
          f"({completos.index[0].date()} a {completos.index[-1].date()})")
