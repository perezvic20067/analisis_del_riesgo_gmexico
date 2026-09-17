"""
Crecimiento anual real del PIB de México (series originales, INEGI).
2025 y 2026 son estimación puntual de Banxico (Informe Trimestral II-2025).
Fuente: Banco de México, "Panorama Macroeconómico en México".
"""
import pandas as pd

PIB_ANIOS = list(range(2000, 2027))
PIB_CRECIMIENTO = [
    5.0, -0.5, -0.2, 1.2, 3.6, 2.1, 4.8, 2.1, 0.9, -6.3,
    5.0, 3.4, 3.6, 0.9, 2.5, 2.7, 1.8, 1.9, 2.0, -0.4,
    -8.4, 6.0, 3.7, 3.4, 1.4, 0.6, 1.1
]

def get_pib_series():
    return pd.Series(PIB_CRECIMIENTO, index=PIB_ANIOS, name="pib_crecimiento_pct")