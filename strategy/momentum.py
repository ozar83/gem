import pandas as pd
from config import fmt_float

def calculate_momentum(df: pd.DataFrame, months: int) -> float:
    """
    Oblicza momentum jako procentową zmianę ceny
    względem ceny sprzed X miesięcy.
    """

    if len(df) < months + 1:
        raise ValueError(
            f"Za mało danych do obliczenia {months}M momentum"
        )

    current_price = df["Close"].iloc[-1]
    past_price = df["Close"].iloc[-(months + 1)]

    momentum = (current_price / past_price) - 1

    return fmt_float(momentum)


def calculate_all_momentums(df: pd.DataFrame) -> dict:
    """
    Zwraca momentum 3M, 6M i 12M jako słownik.
    """

    return {
        "3M": calculate_momentum(df, 3),
        "6M": calculate_momentum(df, 6),
        "12M": calculate_momentum(df, 12),
    }


def compare_assets(df1: pd.DataFrame, df2: pd.DataFrame) -> dict:
    """
    Porównuje dwa aktywa na podstawie 12M momentum.
    Zwraca strukturę z wynikami i wskazaniem zwycięzcy.
    """

    mom1 = calculate_momentum(df1, 12)
    mom2 = calculate_momentum(df2, 12)

    if mom1 > mom2:
        winner = "ASSET_1"
    elif mom2 > mom1:
        winner = "ASSET_2"
    else:
        winner = "TIE"

    return {
        "asset_1_momentum": mom1,
        "asset_2_momentum": mom2,
        "winner": winner
    }