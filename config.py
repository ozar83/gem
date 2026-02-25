# config.py
# Konfiguracja globalna GEM-APP

from datetime import date

# Tickery domyślne GEM
TICKERS = {
    "US_equity": "SPY",
    "exUS_equity": "VEU",
    "bonds": "BND"
}

# Horyzonty momentum w miesiącach
MOMENTUM_PERIODS = [3, 6, 12]

# Źródła danych
DATA_SOURCES = ["yahoo", "stooq"]

# Cache danych (CSV)
DATA_RAW_PATH = "C:/Projects/GEM-APP/data/raw"
DATA_PROCESSED_PATH = "C:/Projects/GEM-APP/data/processed"

# Rebalancing (ostatni dzień miesiąca)
REBALANCE_DAY = "last"  # 'last' lub 'first'

# Start danych historycznych
START_DATE = "2025-01-01"

# end_date = dzisiaj
END_DATE = date.today().strftime("%Y-%m-%d")

# Format daty
DATE_FORMAT = "%Y-%m-%d"

#Interwał
INTERVAL = "1d" # "1d", "1wk", "1mo"

#Precyzja
DECIMALS = 6

def fmt_float(x): return float(f"{x:.{DECIMALS}f}")