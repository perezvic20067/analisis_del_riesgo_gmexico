import yfinance as yf
import pandas as pd
import os

def fetch_historical_data(ticker, filename):

    # Usamos yf.Ticker().history() que es mas estable y evita errores de columnas
    stock = yf.Ticker(ticker)
    raw_data = stock.history(period="max")

    # Verificamos que la tabla no este vacia por fallos de red
    if raw_data.empty:
        print(f"Error: No data found for {ticker}")
        return None

    # history() ya entrega la columna 'Close' ajustada por splits y dividendos
    clean_data = raw_data[['Close']].copy()
    clean_data.columns = ['adj_close']
    clean_data = clean_data.dropna()

    # Limpiamos la zona horaria de la fecha para evitar problemas
    if clean_data.index.tz is not None:
        clean_data.index = clean_data.index.tz_localize(None)

    # Ruta para guardar el archivo
    save_path = os.path.join("..", "datos_historicos", f"{filename}.csv")

    clean_data.to_csv(save_path)
    print(f"Data successfully saved to {save_path}")

    return clean_data


if __name__ == "__main__":
    df_gmexico = fetch_historical_data("GMEXICOB.MX", "gmexico_prices")
    df_ipc = fetch_historical_data("^MXX", "ipc_prices")

print("\nPrimeros 5 días del precio:")
print(df_gmexico.head())
# Ejecuta la funcion para el ticker del IPC mexicano
df_ipc = fetch_historical_data("^MXX", "ipc_prices")
