# Dokumentacja modułu: strategy/gem.py

## Cel modułu
Moduł implementuje strategię Global Equity Momentum (GEM). Jest to strategia inwestycyjna oparta na dwóch filarach:
1.  **Momentum relatywne**: Wybór aktywa o wyższej stopie zwrotu spośród dwóch ryzykownych aktywów (np. akcje USA vs akcje rynków wschodzących).
2.  **Momentum absolutne**: Filtr trendu. Jeśli wybrane ryzykowne aktywo ma ujemną stopę zwrotu (momentum < 0), strategia przechodzi do aktywa bezpiecznego (np. obligacje).

## Klasa `GEM`

Główna klasa odpowiedzialna za logikę decyzyjną strategii.

### Inicjalizacja `__init__`

```python
def __init__(self, data_service: Any)
```

-   **Argumenty**:
    -   `data_service`: Obiekt serwisu danych (np. `DataService`), który udostępnia metodę `get_data(ticker)`. Służy do pobierania historycznych danych cenowych.

### Metoda `evaluate`

Oblicza sygnał strategii GEM dla pojedynczego okresu momentum.

```python
def evaluate(
    self,
    asset_a: str,
    asset_b: str,
    defensive_asset: str,
    period: str,
) -> Dict[str, Any]
```

-   **Argumenty**:
    -   `asset_a`: Ticker pierwszego ryzykownego aktywa (np. "SPY").
    -   `asset_b`: Ticker drugiego ryzykownego aktywa (np. "VEU").
    -   `defensive_asset`: Ticker aktywa bezpiecznego (np. "AGG").
    -   `period`: Klucz okresu momentum zdefiniowany w `config.MOMENTUM_PERIODS` (np. "12m").

-   **Zwraca**:
    Słownik (`Dict[str, Any]`) zawierający szczegóły decyzji:
    -   `period`: Użyty okres momentum.
    -   `asset_a`: Ticker aktywa A.
    -   `asset_a_momentum`: Obliczone momentum dla aktywa A.
    -   `asset_b`: Ticker aktywa B.
    -   `asset_b_momentum`: Obliczone momentum dla aktywa B.
    -   `winner`: Ticker zwycięskiego aktywa (to, w które należy zainwestować).
    -   `winner_momentum`: Momentum zwycięskiego aktywa ryzykownego (lub `None` w przypadku przejścia do defensywy).
    -   `signal_type`: Typ sygnału: `"risk_on"` (inwestycja w akcje) lub `"risk_off"` (ucieczka do obligacji).

-   **Logika działania**:
    1.  Pobiera dane historyczne dla `asset_a` i `asset_b` za pomocą `data_service`.
    2.  Oblicza momentum dla obu aktywów dla zadanego okresu (`period`).
    3.  **Momentum relatywne**: Porównuje momentum A i B. Wygrywa aktywo z wyższym momentum.
    4.  **Momentum absolutne**: Sprawdza, czy momentum zwycięzcy jest dodatnie (> 0).
        -   Jeśli tak: `winner` to zwycięskie aktywo ryzykowne (`signal_type="risk_on"`).
        -   Jeśli nie: `winner` to `defensive_asset` (`signal_type="risk_off"`).

-   **Wyjątki**:
    -   `ValueError`: Jeśli podany `period` nie istnieje w `config.MOMENTUM_PERIODS`.

### Metoda `evaluate_all`

Uruchamia ewaluację strategii dla wszystkich okresów zdefiniowanych w konfiguracji.

```python
def evaluate_all(
    self,
    asset_a: str,
    asset_b: str,
    defensive_asset: str,
) -> Dict[str, Dict[str, Any]]
```

-   **Argumenty**:
    -   `asset_a`, `asset_b`, `defensive_asset`: Tickery aktywów (jak w `evaluate`).

-   **Zwraca**:
    Słownik, gdzie kluczem jest nazwa okresu (np. "12m"), a wartością słownik wyników z metody `evaluate`.

-   **Działanie**:
    Iteruje po wszystkich kluczach w `config.MOMENTUM_PERIODS` i dla każdego wywołuje `evaluate`.

## Zależności
-   `config.MOMENTUM_PERIODS`: Słownik definiujący dostępne okresy momentum.
-   `strategy.momentum.get_momentum`: Funkcja obliczająca momentum.

## Przykłady użycia

```python
# Zakładamy, że data_service jest już zainicjalizowany
gem = GEM(data_service)

# Ewaluacja dla okresu 12 miesięcy
result = gem.evaluate("SPY", "VEU", "AGG", period="12m")
print(f"Winner: {result['winner']}, Signal: {result['signal_type']}")

# Ewaluacja dla wszystkich okresów
all_results = gem.evaluate_all("SPY", "VEU", "AGG")
for period, res in all_results.items():
    print(f"Period {period}: Invest in {res['winner']}")
```
