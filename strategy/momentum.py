import pandas as pd
from typing import Dict

from config import MOMENTUM_PERIODS


def _get_price_column(df: pd.DataFrame) -> str:
    """
    Returns the column name used for momentum calculation.
    Prefers 'Adj Close', falls back to 'Price'.
    """
    if "Adj Close" in df.columns:
        return "Adj Close"
    if "Price" in df.columns:
        return "Price"
    raise ValueError("DataFrame must contain 'Adj Close' or 'Price' column.")


def _validate_data_length(df: pd.DataFrame, required_period: int) -> None:
    """
    Ensures there is enough data to calculate momentum.
    """
    if len(df) <= required_period:
        raise ValueError(
            f"Not enough data to calculate {required_period} month momentum."
        )


def get_momentum(df: pd.DataFrame, period: str) -> float:
    """
    Returns the latest momentum value for a given period.

    Parameters
    ----------
    df : pd.DataFrame
        Monthly price data for a single ticker.
    period : str
        Momentum key defined in config.MOMENTUM_PERIODS (e.g. '3m', '6m', '12m').

    Returns
    -------
    float
        Latest momentum value.
    """

    if period not in MOMENTUM_PERIODS:
        raise ValueError(
            f"Invalid period '{period}'. Allowed values: {list(MOMENTUM_PERIODS.keys())}"
        )

    months = MOMENTUM_PERIODS[period]
    price_col = _get_price_column(df)

    _validate_data_length(df, months)

    momentum_series = df[price_col] / df[price_col].shift(months) - 1
    momentum_value = momentum_series.iloc[-1]

    if pd.isna(momentum_value):
        raise ValueError(
            f"Momentum calculation resulted in NaN for period {period}."
        )

    return float(momentum_value)


def get_all_momentums(df: pd.DataFrame) -> Dict[str, float]:
    """
    Returns latest momentum values for all configured periods.

    Parameters
    ----------
    df : pd.DataFrame
        Monthly price data for a single ticker.

    Returns
    -------
    Dict[str, float]
        Dictionary with momentum values for each configured period.
    """

    results = {}

    for period in MOMENTUM_PERIODS.keys():
        results[period] = get_momentum(df, period)

    return results

import pandas as pd
# from config import fmt_float
#
# def calculate_momentum(df: pd.DataFrame, months: int) -> float:
#     """
#     Oblicza momentum jako procentową zmianę ceny
#     względem ceny sprzed X miesięcy.
#     """
#
#     if len(df) < months + 1:
#         raise ValueError(
#             f"Za mało danych do obliczenia {months}M momentum"
#         )
#
#     current_price = df["Close"].iloc[-1]
#     past_price = df["Close"].iloc[-(months + 1)]
#
#     momentum = (current_price / past_price) - 1
#
#     return fmt_float(momentum)
#
#
# def calculate_all_momentums(df: pd.DataFrame) -> dict:
#     """
#     Zwraca momentum 3M, 6M i 12M jako słownik.
#     """
#
#     return {
#         "3M": calculate_momentum(df, 3),
#         "6M": calculate_momentum(df, 6),
#         "12M": calculate_momentum(df, 12),
#     }
#
#
# def compare_assets(df1: pd.DataFrame, df2: pd.DataFrame) -> dict:
#     """
#     Porównuje dwa aktywa na podstawie 12M momentum.
#     Zwraca strukturę z wynikami i wskazaniem zwycięzcy.
#     """
#
#     mom1 = calculate_momentum(df1, 12)
#     mom2 = calculate_momentum(df2, 12)
#
#     if mom1 > mom2:
#         winner = "ASSET_1"
#     elif mom2 > mom1:
#         winner = "ASSET_2"
#     else:
#         winner = "TIE"
#
#     return {
#         "asset_1_momentum": mom1,
#         "asset_2_momentum": mom2,
#         "winner": winner
#     }