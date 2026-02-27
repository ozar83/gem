from typing import Dict, Any
import pandas as pd
from config import MOMENTUM_PERIODS
from strategy.momentum import get_momentum


class GEM:
    def __init__(self, data_service: Any):
        """
        Initialize the GEM strategy.

        Args:
            data_service: An object capable of fetching asset data via get_data().
        """
        self.data_service = data_service

    def evaluate(
        self,
        asset_a: str,
        asset_b: str,
        defensive_asset: str,
        period: str,
        decision_date: str,
    ) -> Dict[str, Any]:
        """
        Evaluate GEM signal for given assets and momentum period.

        Args:
            asset_a: Ticker for the first risky asset (e.g., SPY).
            asset_b: Ticker for the second risky asset (e.g., VEU).
            defensive_asset: Ticker for the defensive asset (e.g., BND).
            period: Momentum period key (e.g., '3m', '6m', '12m').
            decision_date: The date when the investment decision is made (e.g., '2025-03-01').
                           Data available UP TO the end of the previous month will be used.
        """

        if period not in MOMENTUM_PERIODS:
            raise ValueError(f"Unsupported period: {period}")

        months = MOMENTUM_PERIODS[period]

        # Determine the cutoff date (end of the month prior to decision_date)
        decision_dt = pd.to_datetime(decision_date)
        # We need data up to the last day of the previous month relative to decision_date
        # Example: decision_date = 2025-03-01 -> we need data up to 2025-02-28
        cutoff_date = decision_dt.replace(day=1) - pd.Timedelta(days=1)

        # Fetch monthly data
        # Note: We fetch data starting earlier to ensure we have enough history for momentum calculation
        # The data_service handles the start_date logic based on momentum window,
        # but here we explicitly request monthly data.
        df_a = self.data_service.get_monthly_data(asset_a)
        df_b = self.data_service.get_monthly_data(asset_b)

        # Filter data to include only available history up to cutoff_date
        df_a = df_a[df_a["Date"] <= cutoff_date]
        df_b = df_b[df_b["Date"] <= cutoff_date]

        # Calculate momentum
        momentum_a = get_momentum(df_a, period)
        momentum_b = get_momentum(df_b, period)

        # Relative momentum (winner selection)
        if momentum_a >= momentum_b:
            winner = asset_a
            winner_momentum = momentum_a
        else:
            winner = asset_b
            winner_momentum = momentum_b

        # Absolute momentum filter
        if winner_momentum > 0:
            signal_type = "risk_on"
        else:
            winner = defensive_asset
            winner_momentum = None
            signal_type = "risk_off"

        return {
            "period": period,
            "decision_date": decision_date,
            "asset_a": asset_a,
            "asset_a_momentum": momentum_a,
            "asset_b": asset_b,
            "asset_b_momentum": momentum_b,
            "winner": winner,
            "winner_momentum": winner_momentum,
            "signal_type": signal_type,
        }

    def evaluate_all(
        self,
        asset_a: str,
        asset_b: str,
        defensive_asset: str,
        decision_date: str,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Evaluate GEM for all configured momentum periods.
        """

        results = {}

        for period in MOMENTUM_PERIODS.keys():
            results[period] = self.evaluate(
                asset_a=asset_a,
                asset_b=asset_b,
                defensive_asset=defensive_asset,
                period=period,
                decision_date=decision_date,
            )

        return results