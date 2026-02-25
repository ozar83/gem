from services.data_service import get_data
from strategy.gem import gem_decision

assets = {
    "equity_us": get_data("SPY", interval="1mo", start_date="2020-01-01"),
    "equity_exus": get_data("ACWX", interval="1mo", start_date="2020-01-01"),
    "defensive": get_data("BND", interval="1mo", start_date="2020-01-01"),
}

decision = gem_decision(assets)

print("Wybrane:", decision["decisions"])
print("Momentum:", decision["momentums"])