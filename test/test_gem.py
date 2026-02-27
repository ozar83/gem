import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from strategy.gem import GEM

class TestGEM(unittest.TestCase):
    def setUp(self):
        """
        Przygotowanie środowiska przed każdym testem.
        """
        # Tworzymy fałszywy serwis danych
        self.mock_data_service = MagicMock()
        
        # Inicjalizujemy strategię z mockiem
        self.gem = GEM(self.mock_data_service)
        
        # Przykładowe aktywa
        self.asset_a = "SPY"
        self.asset_b = "QQQ"
        self.defensive = "AGG"
        self.decision_date = "2025-01-01"
        
        # Pusty DataFrame z poprawnym typem kolumny Date (datetime64[ns])
        # Zapobiega to błędowi TypeError przy porównywaniu z Timestamp
        self.empty_df = pd.DataFrame({'Date': pd.Series(dtype='datetime64[ns]')})

    @patch('strategy.gem.get_momentum')
    def test_evaluate_risk_on_asset_a_wins(self, mock_get_momentum):
        """
        Scenariusz: Asset A ma wyższe momentum niż B, i jest ono dodatnie.
        Oczekiwane: Wygrywa A, sygnał Risk On.
        """
        # Konfiguracja mocka: pierwsze wywołanie dla A (0.10), drugie dla B (0.05)
        mock_get_momentum.side_effect = [0.10, 0.05]
        
        # Symulacja zwracania pustych DataFrame (nie są używane, bo mockujemy get_momentum)
        # Teraz używamy get_monthly_data
        self.mock_data_service.get_monthly_data.return_value = self.empty_df

        # Wywołanie metody evaluate
        result = self.gem.evaluate(
            self.asset_a, self.asset_b, self.defensive, period='12m', decision_date=self.decision_date
        )

        # Asercje
        self.assertEqual(result['winner'], self.asset_a)
        self.assertEqual(result['signal_type'], 'risk_on')
        self.assertEqual(result['winner_momentum'], 0.10)
        
        # Sprawdzenie czy pobrano dane dla obu aktywów
        self.mock_data_service.get_monthly_data.assert_any_call(self.asset_a)
        self.mock_data_service.get_monthly_data.assert_any_call(self.asset_b)

    @patch('strategy.gem.get_momentum')
    def test_evaluate_risk_on_asset_b_wins(self, mock_get_momentum):
        """
        Scenariusz: Asset B ma wyższe momentum niż A, i jest ono dodatnie.
        Oczekiwane: Wygrywa B, sygnał Risk On.
        """
        # A = 0.05, B = 0.15
        mock_get_momentum.side_effect = [0.05, 0.15]
        self.mock_data_service.get_monthly_data.return_value = self.empty_df

        # Wywołanie metody evaluate
        result = self.gem.evaluate(
            self.asset_a, self.asset_b, self.defensive, period='12m', decision_date=self.decision_date
        )

        # Sprawdzenie czy wygrało aktywo B
        self.assertEqual(result['winner'], self.asset_b)
        self.assertEqual(result['signal_type'], 'risk_on')
        self.assertEqual(result['winner_momentum'], 0.15)

    @patch('strategy.gem.get_momentum')
    def test_evaluate_risk_off(self, mock_get_momentum):
        """
        Scenariusz: Asset A jest lepszy od B, ale OBA są na minusie.
        Oczekiwane: Wygrywa aktywo defensywne, sygnał Risk Off.
        """
        # A = -0.05, B = -0.10. A > B, ale A < 0.
        mock_get_momentum.side_effect = [-0.05, -0.10]
        self.mock_data_service.get_monthly_data.return_value = self.empty_df

        # Wywołanie metody evaluate
        result = self.gem.evaluate(
            self.asset_a, self.asset_b, self.defensive, period='12m', decision_date=self.decision_date
        )

        # Sprawdzenie czy wygrało aktywo defensywne
        self.assertEqual(result['winner'], self.defensive)
        self.assertEqual(result['signal_type'], 'risk_off')
        self.assertIsNone(result['winner_momentum'])

    def test_evaluate_invalid_period(self):
        """
        Scenariusz: Podano okres, którego nie ma w konfiguracji.
        Oczekiwane: ValueError.
        """
        # Sprawdzenie czy rzucany jest wyjątek dla nieprawidłowego okresu
        with self.assertRaises(ValueError):
            self.gem.evaluate(
                self.asset_a, self.asset_b, self.defensive, period='INVALID_PERIOD', decision_date=self.decision_date
            )

    @patch('strategy.gem.get_momentum')
    def test_evaluate_all(self, mock_get_momentum):
        """
        Scenariusz: Uruchomienie dla wszystkich okresów zdefiniowanych w configu.
        Oczekiwane: Słownik wyników dla każdego klucza.
        """
        # MOMENTUM_PERIODS = {"3m": 3, "6m": 6, "12m": 12}

        mock_get_momentum.side_effect = [
            0.02, 0.01,  # 3m
            0.05, 0.08,  # 6m
            -0.1, -0.2   # 12m
        ]
        self.mock_data_service.get_monthly_data.return_value = self.empty_df

        # Wywołanie metody evaluate_all
        results = self.gem.evaluate_all(
            self.asset_a, self.asset_b, self.defensive, decision_date=self.decision_date
        )

        # Sprawdzamy czy mamy wyniki dla wszystkich kluczy
        self.assertIn('3m', results)
        self.assertIn('6m', results)
        self.assertIn('12m', results)

        # Weryfikacja logiki dla 3 miesięcy
        self.assertEqual(results['3m']['winner'], self.asset_a)
        self.assertEqual(results['3m']['signal_type'], 'risk_on')

        # Weryfikacja logiki dla 6 miesięcy
        self.assertEqual(results['6m']['winner'], self.asset_b)
        self.assertEqual(results['6m']['signal_type'], 'risk_on')

        # Weryfikacja logiki dla 12 miesięcy
        self.assertEqual(results['12m']['winner'], self.defensive)
        self.assertEqual(results['12m']['signal_type'], 'risk_off')

if __name__ == '__main__':
    unittest.main()