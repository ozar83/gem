# data_service.py
# Centralny moduł dostępu do danych rynkowych.
# Odpowiada za:
# - wybór źródła danych (Yahoo / Stooq)
# - fallback w przypadku błędu
# - ujednolicenie formatu danych

import pandas as pd
from services.yahoo_client import fetch_yahoo_data
from utils.dates import calculate_required_start_date
from config import START_DATE, MOMENTUM_PERIODS
# stooq_client dodamy w kolejnym kroku
# from services.stooq_client import fetch_stooq_data


def get_data(
    ticker: str,
    source: str = "yahoo",
    start_date: str = None,
    interval: str = None,
) -> pd.DataFrame:
    """
    Główna funkcja do pobierania danych historycznych.

    :param ticker: symbol instrumentu (np. SPY)
    :param source: źródło danych ("yahoo" lub "stooq")
    :param start_date: data początkowa (jeśli None → użyje config.START_DATE)
    :param interval: interwał resamplingu (np. "M", "W"), domyślnie None (dzienne)
    :return: DataFrame z kolumną 'Date' oraz kolumnami cenowymi (Price, Open, Close, Adj Close, Low, High, Volume)
    """

    try:
        # ==========================
        # WYBÓR ŹRÓDŁA DANYCH
        # ==========================

        decision_start = start_date or START_DATE
        momentum_window = max(MOMENTUM_PERIODS.values())

        required_start = calculate_required_start_date(
            decision_start,
            momentum_window
        )

        if source.lower() == "yahoo":
            df = fetch_yahoo_data(
                ticker=ticker,
                start_date=required_start.date(),
                resample_interval=interval
            )

        # W przyszłości dodamy Stooq
        # elif source.lower() == "stooq":
        #     df = fetch_stooq_data(...)

        else:
            raise ValueError(f"Nieznane źródło danych: {source}")

        # ==========================
        # UJEDNOLICENIE FORMATU
        # ==========================

        # Upewnij się, że mamy kolumnę 'Date' (źródła często zwracają ją jako indeks)
        if "Date" not in df.columns:
            # Jeśli index to DatetimeIndex lub nazywa się 'Date', przenieś go do kolumny
            if isinstance(df.index, pd.DatetimeIndex) or df.index.name in (None, "Date"):
                df = df.reset_index()
                # Gdy indeks był nienazwany, pandas tworzy kolumnę 'index' → zmień na 'Date'
                if "index" in df.columns:
                    df = df.rename(columns={"index": "Date"})

        # Sortowanie po dacie (bezpiecznik)
        df = df.sort_values("Date")

        # Usunięcie ewentualnych duplikatów po dacie
        df = df.drop_duplicates(subset=["Date"])

        # Reset indeksu po sortowaniu
        df = df.reset_index(drop=True)

        return df

    except Exception as e:
        print(f"[DataService] Błąd pobierania danych dla {ticker}: {e}")
        raise


def get_monthly_data(
    ticker: str,
    source: str = "yahoo",
    start_date: str = None,
) -> pd.DataFrame:
    """
    Pobiera dane dzienne i wykonuje resampling do interwału miesięcznego.
    Zwraca ostatnią cenę z każdego miesiąca.
    """
    return get_data(ticker, source, start_date, interval="M")
