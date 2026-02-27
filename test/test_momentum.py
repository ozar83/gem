import pandas as pd
import pytest
from services.data_service import get_data, get_monthly_data
from strategy.momentum import get_momentum, get_all_momentums
from config import MOMENTUM_PERIODS

# --- Testy na danych syntetycznych (istniejące) ---

def create_test_dataframe():
    """
    Creates deterministic monthly price data.
    Length = max_period + 1 to allow momentum calculation.
    """
    max_months = max(MOMENTUM_PERIODS.values())
    periods = max_months + 1

    dates = pd.date_range(start="2023-01-31", periods=periods, freq="M")
    prices = [100 + i * 10 for i in range(periods)]

    df = pd.DataFrame(
        {"Adj Close": prices},
        index=dates
    )

    return df


def test_get_momentum_for_all_periods():
    df = create_test_dataframe()

    last_price = df["Adj Close"].iloc[-1]

    for period_name, months in MOMENTUM_PERIODS.items():
        result = get_momentum(df, period_name)

        past_price = df["Adj Close"].iloc[-(months + 1)]
        expected = (last_price / past_price) - 1

        assert pytest.approx(result, rel=1e-6) == expected


def test_get_all_momentums_returns_all_configured_periods():
    df = create_test_dataframe()

    result = get_all_momentums(df)

    assert set(result.keys()) == set(MOMENTUM_PERIODS.keys())

    for value in result.values():
        assert isinstance(value, float)


def test_invalid_period():
    df = create_test_dataframe()

    with pytest.raises(ValueError):
        get_momentum(df, "INVALID_PERIOD")


def test_not_enough_data():
    max_months = max(MOMENTUM_PERIODS.values())
    df = create_test_dataframe().iloc[:max_months - 1]

    # testujemy największy okres
    largest_period = max(MOMENTUM_PERIODS, key=MOMENTUM_PERIODS.get)

    with pytest.raises(ValueError):
        get_momentum(df, largest_period)


def test_fallback_to_price_column():
    df = create_test_dataframe()
    df = df.rename(columns={"Adj Close": "Price"})

    result = get_all_momentums(df)

    for period_name in MOMENTUM_PERIODS.keys():
        assert isinstance(result[period_name], float)

def test_momentum_3m():
    df = create_test_dataframe()
    result = get_momentum(df, "3m")

    months = MOMENTUM_PERIODS["3m"]
    last_price = df["Adj Close"].iloc[-1]
    past_price = df["Adj Close"].iloc[-(months + 1)]
    expected = (last_price / past_price) - 1

    assert pytest.approx(result, rel=1e-6) == expected


def test_momentum_6m():
    df = create_test_dataframe()
    result = get_momentum(df, "6m")

    months = MOMENTUM_PERIODS["6m"]
    last_price = df["Adj Close"].iloc[-1]
    past_price = df["Adj Close"].iloc[-(months + 1)]
    expected = (last_price / past_price) - 1

    assert pytest.approx(result, rel=1e-6) == expected


def test_momentum_12m():
    df = create_test_dataframe()
    result = get_momentum(df, "12m")

    months = MOMENTUM_PERIODS["12m"]
    last_price = df["Adj Close"].iloc[-1]
    past_price = df["Adj Close"].iloc[-(months + 1)]
    expected = (last_price / past_price) - 1

    assert pytest.approx(result, rel=1e-6) == expected

def test_print_single_momentum():
    df = create_test_dataframe()

    result = get_momentum(df, "12m")

    print("\n=== PRINT TEST 12M MOMENTUM ===")
    print(f"12m momentum: {result:.6f}")

    assert isinstance(result, float)

# --- Nowy test na danych rzeczywistych ---

def test_real_data_momentum_and_print():
    """
    Pobiera rzeczywiste dane dla SPY i oblicza momentum dla wszystkich okresów.
    Wyniki są wypisywane na konsolę.
    """
    ticker = "SPY"
    print(f"\n=== REAL DATA MOMENTUM TEST FOR {ticker} ===")
    
    # Pobieramy dane miesięczne bezpośrednio z data_service
    # Zakładamy, że data_service działa poprawnie i zwraca DataFrame
    df_monthly = get_monthly_data(ticker, start_date="2020-01-01")
    
    # Upewniamy się, że mamy dane
    assert not df_monthly.empty, "Pobrany DataFrame jest pusty!"
    
    # Obliczamy momentum dla wszystkich okresów
    momentums = get_all_momentums(df_monthly)
    
    # Używamy ostatniej daty z danych miesięcznych
    actual_last_date = df_monthly["Date"].iloc[-1]
    print(f"Momentum obliczone dla daty (ostatnia cena): {actual_last_date.strftime('%Y-%m-%d')}")
    print("Obliczone momentum:")
    for period, value in momentums.items():
        print(f"  {period}: {value:.4f} ({value*100:.2f}%)")
        
    # Podstawowe asercje
    assert isinstance(momentums, dict)
    assert len(momentums) == len(MOMENTUM_PERIODS)
    
    print("=== END REAL DATA TEST ===\n")