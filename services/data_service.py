# data_service.py
# Centralny moduł dostępu do danych rynkowych.
# Odpowiada za:
# - wybór źródła danych (Yahoo / Stooq)
# - fallback w przypadku błędu
# - ujednolicenie formatu danych

import pandas as pd
from services.yahoo_client import fetch_yahoo_data
from utils.dates import calculate_required_start_date
# stooq_client dodamy w kolejnym kroku
# from services.stooq_client import fetch_stooq_data


def get_data(
    ticker: str,
    source: str = "yahoo",
    start_date: str = None,
    end_date: str = None,
    interval: str = "1mo"
) -> pd.DataFrame:
    """
    Główna funkcja do pobierania danych historycznych.

    :param ticker: symbol instrumentu (np. SPY)
    :param source: źródło danych ("yahoo" lub "stooq")
    :param start_date: data początkowa (jeśli None → użyje config)
    :param end_date: data końcowa (jeśli None → użyje config)
    :param interval: interwał danych ("1d", "1wk", "1mo")
    :return: DataFrame z kolumnami:
             - Date (datetime)
             - Close (float)
    """

    try:
        # ==========================
        # WYBÓR ŹRÓDŁA DANYCH
        # ==========================

        momentum_window = 12 #do zmiany na 3,6,12

        required_start = calculate_required_start_date(
            start_date,
            momentum_window
        )

        print("Musimy pobrać dane od:", required_start.date())

        if source.lower() == "yahoo":
            df = fetch_yahoo_data(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                interval=interval
            )

        # W przyszłości dodamy Stooq
        # elif source.lower() == "stooq":
        #     df = fetch_stooq_data(...)

        else:
            raise ValueError(f"Nieznane źródło danych: {source}")

        # ==========================
        # UJEDNOLICENIE FORMATU
        # ==========================

        # Sortowanie po dacie (bezpiecznik)
        df = df.sort_values("Date")

        # Usunięcie ewentualnych duplikatów
        df = df.drop_duplicates(subset=["Date"])

        # Reset indeksu po sortowaniu
        df = df.reset_index(drop=True)

        return df

    except Exception as e:
        print(f"[DataService] Błąd pobierania danych dla {ticker}: {e}")
        raise