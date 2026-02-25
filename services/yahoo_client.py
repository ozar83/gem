# yahoo_client.py

import os
import pandas as pd
import yfinance as yf
from datetime import datetime
from config import DATA_RAW_PATH

# Jawna definicja struktury CSV
CSV_COLUMNS = ["Date", "Price", "Open", "Close", "Adj Close", "Low", "High", "Volume"]


def fetch_yahoo_data(
        ticker: str,
        start_date: str,
        resample_interval: str = None  # np. "M", "W", None
) -> pd.DataFrame:
    """
    Pobiera i cache'uje dane dzienne (1d) z Yahoo Finance w podziale rocznym.

    - Dane w plikach zawsze w interwale 1d.
    - Aktualizowany jest tylko bieżący rok.
    - Zwraca dane od start_date do teraz.
    - Opcjonalnie wykonuje resampling lokalnie.
    - Strukturę pliku CSV definiuje CSV_COLUMNS.
    """

    start_dt = pd.to_datetime(start_date)
    current_year = datetime.now().year
    start_year = start_dt.year

    os.makedirs(DATA_RAW_PATH, exist_ok=True)

    all_data = []

    for year in range(start_year, current_year + 1):

        file_path = os.path.join(DATA_RAW_PATH, f"{ticker}_{year}.csv")

        year_start = datetime(year, 1, 1)
        year_end = datetime.now() if year == current_year else datetime(year, 12, 31)

        # --------------------------------------------------
        # PLIK ISTNIEJE
        # --------------------------------------------------
        if os.path.exists(file_path):

            df_existing = pd.read_csv(file_path, parse_dates=["Date"], index_col="Date")

            # Aktualizacja bieżącego roku
            if year == current_year:
                last_date = df_existing.index.max()

                if last_date < pd.to_datetime(datetime.now().date()):
                    print(f"Updating {ticker} {year}")

                    df_new = yf.download(
                        ticker,
                        start=last_date + pd.Timedelta(days=1),
                        interval="1d",
                        progress=False
                    )

                    if not df_new.empty:
                        # Mapowanie danych z Yahoo na strukturę CSV
                        df_new = _map_yahoo_to_csv_structure(df_new)

                        df_existing = pd.concat([df_existing, df_new])
                        df_existing = df_existing[~df_existing.index.duplicated(keep="last")]
                        df_existing.sort_index(inplace=True)
                        df_existing.to_csv(file_path, columns=CSV_COLUMNS[1:], index=True)

            all_data.append(df_existing)

        # --------------------------------------------------
        # PLIK NIE ISTNIEJE
        # --------------------------------------------------
        else:
            print(f"Downloading {ticker} {year}")

            df_year = yf.download(
                ticker,
                start=year_start,
                end=year_end,
                interval="1d",
                progress=False
            )

            if not df_year.empty:
                # Mapowanie danych z Yahoo na strukturę CSV
                df_year = _map_yahoo_to_csv_structure(df_year)
                df_year.to_csv(file_path, columns=CSV_COLUMNS[1:], index=True)

            all_data.append(df_year)

    # --------------------------------------------------
    # SCALANIE
    # --------------------------------------------------
    if not all_data:
        return pd.DataFrame()

    df_final = pd.concat(all_data)
    df_final = df_final[~df_final.index.duplicated(keep="last")]
    df_final.sort_index(inplace=True)

    df_final = df_final[df_final.index >= start_dt]

    # --------------------------------------------------
    # RESAMPLING (opcjonalny)
    # --------------------------------------------------
    if resample_interval:
        df_final = (
            df_final
            .resample(resample_interval)
            .agg({
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Adj Close": "last",
                "Volume": "sum",
                "Price": "last"
            })
            .dropna()
        )

    return df_final


def _map_yahoo_to_csv_structure(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mapuje dane z Yahoo Finance na strukturę zdefiniowaną przez CSV_COLUMNS.

    Yahoo zwraca: Open, High, Low, Close, Adj Close, Volume
    Struktura CSV: Date, Price, Open, Close, Adj Close, Low, High, Volume

    Price = Close (cena zamknięcia)
    """

    # Upewnij się, że Date jest indeksem
    if "Date" in df.columns:
        df = df.set_index("Date")

    # Obsługa MultiIndex columns (gdy yfinance zwraca hierarchiczne kolumny)
    if isinstance(df.columns, pd.MultiIndex):
        # Weź pierwszy poziom MultiIndex (nazwy kolumn OHLCV)
        df.columns = df.columns.get_level_values(0)

    # Obsługa brakujących kolumn
    # Jeśli 'Adj Close' nie istnieje, użyj 'Close'
    if "Adj Close" not in df.columns:
        df["Adj Close"] = df["Close"]

    # Jeśli 'Price' nie istnieje (to wynik naszego mapowania), użyj 'Close'
    if "Price" not in df.columns:
        df["Price"] = df["Close"]

    # Stwórz DataFrame z wymaganymi kolumnami w odpowiedniej kolejności
    # Wybierz tylko potrzebne kolumny
    df_mapped = df[[
        "Price",
        "Open",
        "Close",
        "Adj Close",
        "Low",
        "High",
        "Volume"
    ]].copy()

    return df_mapped