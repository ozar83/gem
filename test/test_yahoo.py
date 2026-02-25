# test_yahoo.py
from services.yahoo_client import fetch_yahoo_data

# Pobranie SPY miesięcznie, domyślnie od START_DATE z config.py
df = fetch_yahoo_data("ISAC.L", "2025-01-01")

# Podgląd pierwszych 5 wierszy
print(df.head())
print(df.tail())