# test_yahoo.py
import pandas as pd
from services.yahoo_client import fetch_yahoo_data

def test_fetch_data_and_print():
    # Pobranie SPY miesięcznie, domyślnie od START_DATE z config.py
    df = fetch_yahoo_data("ISAC.L", "2025-03-01")

    # Podgląd pierwszych 5 wierszy
    print(df.head())
    print(df.tail())

def test_fetch_returns_dataframe():
    df = fetch_yahoo_data("SPY", "2022-01-01")

    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_fetch_respects_start_date():
    start_date = "2023-01-01"
    df = fetch_yahoo_data("SPY", start_date)

    assert df.index.min() >= pd.to_datetime(start_date)


def test_fetch_contains_adj_close():
    df = fetch_yahoo_data("SPY", "2022-01-01")

    assert "Adj Close" in df.columns