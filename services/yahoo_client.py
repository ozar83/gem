# yahoo_client.py
# Moduł odpowiedzialny za pobieranie danych historycznych z Yahoo Finance
# Obsługuje cache CSV w folderze data/raw

import os
import pandas as pd
import yfinance as yf
from config import DATA_RAW_PATH, START_DATE, END_DATE, INTERVAL

def fetch_yahoo_data(ticker: str, start_date: str = None, end_date: str = None, interval: str = None) -> pd.DataFrame:
    """
    Pobiera dane historyczne z Yahoo Finance dla danego instrumentu i zapisuje je w formie CSV cache.

    :param ticker: symbol giełdowy (np. "SPY", "VEU", "BND")
    :param start_date: data początkowa w formacie YYYY-MM-DD. Jeśli None, używa START_DATE z config.py
    :param start_date: data końcowa w formacie YYYY-MM-DD. Jeśli None, używa END_DATE z config.py
    :param interval: częstotliwość danych ("1d", "1wk", "1mo")
    :return: pandas.DataFrame z kolumnami:
             - Date: data
             - Close: cena zamknięcia
    """

    # Jeśli start_date nie został podany, używamy wartości z config.py
    if start_date is None:
        start_date = START_DATE

    if end_date is None:
        end_date = END_DATE

    if interval is None:
        interval = INTERVAL

    # Tworzymy folder do cache jeśli nie istnieje
    os.makedirs(DATA_RAW_PATH, exist_ok=True)

    # Plik CSV, w którym będziemy trzymać cache
    csv_file = os.path.join(DATA_RAW_PATH, f"{ticker}_{start_date}_{end_date}_{interval}.csv")

    # =====================
    # KROK 1: SPRAWDZENIE CACHE
    # =====================
    if os.path.exists(csv_file):
        # Jeśli plik istnieje, wczytujemy dane z CSV zamiast pobierać z internetu
        df = pd.read_csv(csv_file, parse_dates=["Date"])
        print(f"[Yahoo] Załadowano dane z cache dla {ticker} ({interval})")
        return df

    # =====================
    # KROK 2: POBRANIE DANYCH Z YAHOO FINANCE
    # =====================
    print(f"[Yahoo] Pobieranie danych dla {ticker} od {start_date} do {end_date}")
    data = yf.download(ticker, start=start_date, end=end_date, progress=False, interval=interval, auto_adjust=False)

    # Sprawdzenie, czy Yahoo zwróciło dane
    if data.empty:
        raise ValueError(f"[Yahoo] Nie udało się pobrać danych dla {ticker}. Sprawdź ticker i połączenie internetowe.")

    # ===============================
    # NORMALIZACJA STRUKTURY DANYCH
    # ===============================

    # ===============================
    # NORMALIZACJA STRUKTURY DANYCH
    # ===============================

    # Jeśli kolumny są MultiIndex → spłaszcz
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Jeśli Date jest indeksem → przenieś do kolumny
    if data.index.name == "Date" or "Date" not in data.columns:
        data = data.reset_index()

    # Upewnij się że kolumna nazywa się dokładnie "Date"
    if "index" in data.columns:
        data.rename(columns={"index": "Date"}, inplace=True)

    # Sortowanie po dacie
    data = data.sort_values("Date").reset_index(drop=True)

    # =====================
    # KROK 3: PRZYGOTOWANIE DATAFRAME
    # =====================

    # Zachowujemy Date i Close
    df = data[["Date", "Close"]].copy()

    # Reset indeksu bezpieczeństwa
    df = df.reset_index(drop=True)

    # Walidacja
    if "Date" not in df.columns:
        raise ValueError(f"[Yahoo] Brak kolumny Date. Kolumny: {df.columns}")

    # =====================
    # KROK 4: ZAPIS DO CSV CACHE
    # =====================
    df.to_csv(csv_file, index=False)
    print(f"[Yahoo] Zapisano dane do {csv_file}")

    return df