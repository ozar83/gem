# yahoo_client.py

import os
import pandas as pd
import yfinance as yf
from datetime import datetime
from config import DATA_RAW_PATH


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
                        df_existing = pd.concat([df_existing, df_new])
                        df_existing = df_existing[~df_existing.index.duplicated(keep="last")]
                        df_existing.sort_index(inplace=True)
                        df_existing.to_csv(file_path)

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
                df_year.to_csv(file_path)

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
                "Volume": "sum"
            })
            .dropna()
        )

    return df_final