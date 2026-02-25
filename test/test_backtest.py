from services.data_service import get_data
from strategy.backtest import backtest_gem
import plotly.graph_objects as go

start_date = "2015-01-01"
end_date = "2022-01-01"

assets = {
    "equity_us": get_data("SPY", interval="1mo", start_date=start_date, end_date=end_date),
    "equity_exus": get_data("ACWX", interval="1mo", start_date=start_date, end_date=end_date),
    "defensive": get_data("BND", interval="1mo", start_date=start_date, end_date=end_date),
}

results = backtest_gem(assets, start_date)

# print(results.head())
# print(f"Final portfolio value for period from {start_date} to {end_date}: ", results["Portfolio_Value"].iloc[-1])

# equity curve dla 12M
# results["equity_curves"]["12M"].plot(title="GEM 12M Equity Curve")

# Wykres wszystkich horyzontów
# fig = go.Figure()
# for h in ["3M","6M","12M"]:
#     fig.add_trace(go.Scatter(
#         x=results["equity_curves"][h].index,
#         y=results["equity_curves"][h].values,
#         mode="lines",
#         name=f"{h} GEM"
#     ))
# fig.update_layout(title="GEM Equity Curves", xaxis_title="Date", yaxis_title="Portfolio Value", template="plotly_white")
# fig.show()

# statystyki
# print(results["equity_curves"]["12M"])
print(results["statistics"]["3M"])
print(results["statistics"]["6M"])
print(results["statistics"]["12M"])
print(results["decisions"]["3M"])
print(results["decisions"]["6M"])
print(results["decisions"]["12M"])
print(results["tickers"])

