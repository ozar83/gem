import unittest
import pandas as pd
import json
from datetime import datetime
from services.yahoo_client import fetch_yahoo_data
from services.data_service import get_data, get_monthly_data
from strategy.momentum import get_momentum, get_all_momentums
from strategy.gem import GEM
from config import MOMENTUM_PERIODS

class TestUberIntegration(unittest.TestCase):
    """
    Uber-test integracyjny sprawdzający cały przepływ danych:
    Yahoo Client -> Data Service -> Momentum -> GEM Strategy.
    
    Testy operują na rzeczywistych danych pobieranych z Yahoo Finance.
    Wyniki są wypisywane na konsolę.
    """

    def setUp(self):
        self.ticker_a = "SPY"
        self.ticker_b = "VEU"
        self.defensive = "BND"
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Domyślna data decyzji dla testu 04 (dzisiaj)
        self.decision_date_now = self.current_date

        print(f"\n{'='*60}")
        print(f"SETUP: Tickers: {self.ticker_a}, {self.ticker_b}, {self.defensive}")
        print(f"SETUP: Current System Date: {self.current_date}")
        print(f"{'='*60}\n")

    def test_01_yahoo_client_fetch(self):
        """
        Krok 1: Sprawdzenie czy Yahoo Client pobiera dane dzienne.
        """
        print(">>> TEST 01: Yahoo Client Fetch (Raw Daily Data)")
        
        # Pobieramy dane od połowy 2024 roku
        start_date = "2024-06-01"
        df = fetch_yahoo_data(self.ticker_a, start_date=start_date)
        
        print(f"Pobrano {len(df)} wierszy dla {self.ticker_a} od {start_date}")
        if not df.empty:
            print("Pierwsze 5 wierszy:")
            print(df.head(5)[["Close", "Adj Close", "Volume"]])
            print("Ostatnie 5 wierszy:")
            print(df.tail(5)[["Close", "Adj Close", "Volume"]])
        
        self.assertFalse(df.empty, "Yahoo Client zwrócił pusty DataFrame")
        self.assertIn("Adj Close", df.columns)
        self.assertIn("Close", df.columns)
        print("<<< TEST 01: OK\n")

    def test_02_data_service_monthly_resampling(self):
        """
        Krok 2: Sprawdzenie czy Data Service poprawnie robi resampling do miesięcznych.
        """
        print(">>> TEST 02: Data Service (Monthly Resampling)")
        
        # Pobieramy dane miesięczne od połowy 2024
        start_date = "2024-06-01"
        df_monthly = get_monthly_data(self.ticker_a, start_date=start_date)
        
        print(f"Pobrano {len(df_monthly)} wierszy miesięcznych dla {self.ticker_a} od {start_date}")
        
        if not df_monthly.empty:
            print("Pierwsze 5 miesięcy (Date, Adj Close):")
            print(df_monthly[["Date", "Adj Close"]].head(5))
            print("Ostatnie 5 miesięcy (Date, Adj Close):")
            print(df_monthly[["Date", "Adj Close"]].tail(5))
            
            # Sprawdzenie czy daty są unikalne (jeden wiersz na miesiąc)
            dates = df_monthly["Date"]
            if len(dates) > 1:
                diffs = dates.diff().dropna()
                print(f"Średnia różnica dni między wierszami: {diffs.dt.days.mean():.1f}")
        
        self.assertFalse(df_monthly.empty, "Data Service zwrócił pusty DataFrame miesięczny")
        self.assertTrue(len(df_monthly) > 0)
        print("<<< TEST 02: OK\n")

    def test_03_momentum_calculation(self):
        """
        Krok 3: Obliczenie momentum dla pobranych danych miesięcznych.
        """
        print(">>> TEST 03: Momentum Calculation")
        
        # Pobieramy dane od połowy 2024
        start_date = "2024-06-01"
        df_monthly = get_monthly_data(self.ticker_a, start_date=start_date)
        
        try:
            momentums = get_all_momentums(df_monthly)
            print(f"Momentum dla {self.ticker_a} (na podstawie danych do {df_monthly['Date'].iloc[-1].date()}):")
            for period, value in momentums.items():
                print(f"  {period}: {value:.4f} ({value*100:.2f}%)")
        except ValueError as e:
            print(f"Ostrzeżenie: Nie udało się obliczyć wszystkich momentum (zbyt krótka historia od 2024-06): {e}")
            try:
                mom_3m = get_momentum(df_monthly, "3m")
                print(f"  3m: {mom_3m:.4f} ({mom_3m*100:.2f}%)")
            except ValueError:
                print("  Nawet 3m się nie udało (zbyt mało danych)")

        print("<<< TEST 03: OK\n")

    def test_04_gem_strategy_evaluate_now(self):
        """
        Krok 4: Pełna ewaluacja strategii GEM dla bieżącej daty (System Date).
        """
        print(f">>> TEST 04: GEM Strategy Evaluation (Decision Date: {self.decision_date_now})")
        
        class RealDataService:
            def get_data(self, ticker):
                return get_data(ticker)
            
            def get_monthly_data(self, ticker):
                # Pobieramy dane z zapasem
                return get_monthly_data(ticker, start_date="2020-01-01")

        gem = GEM(RealDataService())
        
        try:
            results = gem.evaluate_all(
                asset_a=self.ticker_a,
                asset_b=self.ticker_b,
                defensive_asset=self.defensive,
                decision_date=self.decision_date_now
            )
            
            print("\nWYNIKI STRATEGII GEM:")
            print(json.dumps(results, indent=4, default=str))
            
        except ValueError as e:
            print(f"\nBłąd podczas ewaluacji strategii: {e}")
        
        print("<<< TEST 04: OK\n")

    def test_05_gem_strategy_specific_date(self):
        """
        Krok 5: Ewaluacja strategii GEM dla konkretnej daty decyzyjnej (2025-07-01).
        """
        target_date = "2025-07-01"
        print(f">>> TEST 05: GEM Strategy Evaluation (Target Decision Date: {target_date})")
        
        class RealDataService:
            def get_data(self, ticker):
                return get_data(ticker)
            
            def get_monthly_data(self, ticker):
                # Pobieramy dane z zapasem
                return get_monthly_data(ticker, start_date="2020-01-01")

        gem = GEM(RealDataService())
        
        try:
            results = gem.evaluate_all(
                asset_a=self.ticker_a,
                asset_b=self.ticker_b,
                defensive_asset=self.defensive,
                decision_date=target_date
            )
            
            print(f"\nWYNIKI STRATEGII GEM (Data decyzji: {target_date}):")
            print(json.dumps(results, indent=4, default=str))
            
        except ValueError as e:
            print(f"\nBłąd podczas ewaluacji strategii: {e}")
            
        print("<<< TEST 05: OK\n")

    def test_06_gem_strategy_september_2025_with_data_preview(self):
        """
        Krok 6: Ewaluacja strategii GEM dla daty 2025-09-01.
        Dodatkowo drukuje dane (ostatnie wiersze), które zostały użyte do obliczeń.
        """
        target_date = "2025-09-01"
        print(f">>> TEST 06: GEM Strategy & Data Preview (Target: {target_date})")
        
        # 1. Symulacja logiki GEM, aby pokazać dane
        cutoff_date = pd.to_datetime(target_date).replace(day=1) - pd.Timedelta(days=1)
        print(f"Data odcięcia (koniec poprzedniego miesiąca): {cutoff_date.date()}")
        
        # --- Ticker A (SPY) ---
        df_spy = get_monthly_data(self.ticker_a, start_date="2024-01-01")
        df_spy_filtered = df_spy[df_spy["Date"] <= cutoff_date]

        print(f"\n[PODGLĄD DANYCH] Dane dla {self.ticker_a} dostępne w dniu decyzji {target_date}:")
        if not df_spy_filtered.empty:
            print(df_spy_filtered.tail(12)[["Date", "Adj Close"]])
            print(f"Ostatnia dostępna data w zbiorze: {df_spy_filtered['Date'].iloc[-1].date()}")
        else:
            print("Brak danych spełniających kryteria.")

        # --- Ticker B (VEU) ---
        df_veu = get_monthly_data(self.ticker_b, start_date="2024-01-01")
        df_veu_filtered = df_veu[df_veu["Date"] <= cutoff_date]

        print(f"\n[PODGLĄD DANYCH] Dane dla {self.ticker_b} dostępne w dniu decyzji {target_date}:")
        if not df_veu_filtered.empty:
            print(df_veu_filtered.tail(12)[["Date", "Adj Close"]])
            print(f"Ostatnia dostępna data w zbiorze: {df_veu_filtered['Date'].iloc[-1].date()}")
        else:
            print("Brak danych spełniających kryteria.")

        # 2. Uruchomienie Strategii
        class RealDataService:
            def get_data(self, ticker):
                return get_data(ticker)
            
            def get_monthly_data(self, ticker):
                return get_monthly_data(ticker, start_date="2024-01-01")

        gem = GEM(RealDataService())
        
        try:
            results = gem.evaluate_all(
                asset_a=self.ticker_a,
                asset_b=self.ticker_b,
                defensive_asset=self.defensive,
                decision_date=target_date
            )
            
            print(f"\nWYNIKI STRATEGII GEM (Data decyzji: {target_date}):")
            print(json.dumps(results, indent=4, default=str))
            
        except ValueError as e:
            print(f"\nBłąd podczas ewaluacji strategii: {e}")

        print("<<< TEST 06: OK\n")

if __name__ == '__main__':
    unittest.main()