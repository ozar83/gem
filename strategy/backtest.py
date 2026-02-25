import pandas as pd
import numpy as np
from strategy.gem import gem_decision

def backtest_gem(assets: dict, start_date: str) -> dict:
    """
    Backtest GEM dla wszystkich horyzontów momentum (3M,6M,12M) z dynamicznymi tickerami.

    Args:
        assets: dict w formacie {rola: pd.DataFrame}, gdzie każda rola:
            'equity_us', 'equity_exus', 'defensive'
            i zawiera kolumnę 'Close'.
            Index musi być DatetimeIndex.
        start_date: str, data rozpoczęcia inwestycji (format "YYYY-MM-DD")

    Returns:
        dict:
            {
                "equity_curves": dict {horyzont: pd.Series},
                "monthly_returns": dict {horyzont: pd.Series},
                "statistics": dict {horyzont: statystyki},
                "decisions": dict {horyzont: ticker wybrany przez GEM},
                "tickers": dict {rola: ticker wprowadzony przez użytkownika}
            }
    """

    # 🔹 Walidacja ról
    required_roles = {"equity_us", "equity_exus", "defensive"}
    if set(assets.keys()) != required_roles:
        raise ValueError(f"Assets muszą zawierać dokładnie role: {required_roles}")

    # 🔹 Wyciągamy tickery z DataFrame jeśli użytkownik je podał w atrybucie 'ticker'
    tickers_map = {role: df.attrs.get("ticker", role) for role, df in assets.items()}

    # 🔹 Daty do backtestu (przyjmujemy, że wszystkie aktywa mają te same daty)
    dates = assets["equity_us"].loc[start_date:].index

    momentum_horizons = ["3M", "6M", "12M"]

    # 🏦 Inicjalizacja equity, miesięcznych zwrotów i decyzji
    equity_curves = {h: [] for h in momentum_horizons}
    monthly_returns = {h: [] for h in momentum_horizons}
    portfolio_value = {h: 1.0 for h in momentum_horizons}  # start od 1 jednostki
    decisions = {h: None for h in momentum_horizons}

    # 🔄 Pętla po wszystkich miesiącach
    for current_date in dates:
        # Wycinamy dane do dzisiejszej daty
        current_assets = {role: df.loc[:current_date] for role, df in assets.items()}

        # 🔑 decyzje GEM dla wszystkich horyzontów
        gem_result = gem_decision(current_assets)  # zwraca dict {horyzont: wybrana rola}

        for h in momentum_horizons:
            selected_role = gem_result["decisions"][h]
            selected_df = current_assets[selected_role]

            # obliczenie miesięcznego zwrotu
            if len(selected_df) < 2:
                monthly_return = 0
            else:
                prev_price = selected_df["Close"].iloc[-2]
                current_price = selected_df["Close"].iloc[-1]
                monthly_return = (current_price / prev_price) - 1

            # aktualizacja equity
            portfolio_value[h] *= (1 + monthly_return)
            equity_curves[h].append(portfolio_value[h])
            monthly_returns[h].append(monthly_return)

            # zapamiętujemy ticker decyzji
            decisions[h] = tickers_map[selected_role]

    # zamiana na pd.Series
    equity_curves = {h: pd.Series(v, index=dates) for h, v in equity_curves.items()}
    monthly_returns = {h: pd.Series(v, index=dates) for h, v in monthly_returns.items()}

    # 🧮 Statystyki
    statistics = {}
    for h in momentum_horizons:
        returns = monthly_returns[h]
        total_months = len(returns)

        if total_months == 0:
            cagr = max_drawdown = volatility = sharpe = np.nan
        else:
            cagr = (equity_curves[h].iloc[-1]) ** (12 / total_months) - 1
            max_drawdown = (equity_curves[h] / equity_curves[h].cummax() - 1).min()
            volatility = returns.std() * np.sqrt(12)
            sharpe = cagr / volatility if volatility != 0 else np.nan

        statistics[h] = {
            "CAGR": cagr,                           # roczna stopa zwrotu
            "Max Drawdown": max_drawdown,           # maksymalny spadek portfela
            "Volatility": volatility,               # roczna zmienność portfela
            "Sharpe": sharpe                        # Sharpe ratio
        }

    # 🔹 Zwracamy pełny wynik z tickerami i decyzjami GEM
    return {
        "equity_curves": equity_curves,
        "monthly_returns": monthly_returns,
        "statistics": statistics,
        "decisions": decisions,   # ticker wybrany przez strategię GEM dla 3M/6M/12M
        "tickers": tickers_map    # mapowanie rola -> ticker użytkownika
    }

# equity_curves[h] – jak zmieniała się wartość portfela w czasie dla danego horyzontu (3M,6M,12M)
# monthly_returns[h] – miesięczne zwroty portfela (np. 0.02 = +2%)
# statistics[h]["CAGR"] – roczna stopa zwrotu
# statistics[h]["Max Drawdown"] – największy procentowy spadek portfela od szczytu
# statistics[h]["Volatility"] – roczna zmienność portfela
# statistics[h]["Sharpe"] – wskaźnik ryzyka/zwrotu (im wyższy, tym lepszy stosunek zwrotu do ryzy