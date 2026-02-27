
from services.data_service import get_data

def test_get_data_and_print():
    #Pobranie danych
    print()
    df = get_data("SPY", source="yahoo", start_date="2025-04-01")
    print(df.head())
    print(df.tail())