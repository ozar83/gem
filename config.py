# config.py
# Konfiguracja globalna GEM-APP

from datetime import date
from pathlib import Path

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
# katalog główny projektu (folder, w którym jest config.py)
BASE_DIR = Path(__file__).resolve().parent

# jeśli config.py jest w root projektu → to wystarczy
# jeśli jest np. w src/, dajemy .parent.parent

DATA_RAW_PATH = BASE_DIR / "data" / "raw"
DATA_PROCESSED_PATH = BASE_DIR / "data" / "processed"

# Rebalancing (ostatni dzień miesiąca)
REBALANCE_DAY = "last"  # 'last' lub 'first'

# Start danych historycznych
START_DATE = "2025-01-01"

# Format daty
DATE_FORMAT = "%Y-%m-%d"

#Interwał
INTERVAL = "1d" # "1d", "1wk", "1mo"

#Precyzja
DECIMALS = 6

def fmt_float(x): return float(f"{x:.{DECIMALS}f}")