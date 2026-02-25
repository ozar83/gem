from services.data_service import get_data

df = get_data("SPY", source="yahoo", interval="1d", start_date="2025-04-01")

print(df.head())
print(df.tail())