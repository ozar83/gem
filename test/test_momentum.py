from services.data_service import get_data
from strategy.momentum import calculate_all_momentums, compare_assets

spy = get_data("SPY", interval="1mo", start_date="2020-01-01")
acwi = get_data("ACWX", interval="1mo", start_date="2020-01-01")

print("SPY momentum:", calculate_all_momentums(spy))
print("ACWX momentum:", calculate_all_momentums(acwi))

comparison = compare_assets(spy, acwi)

print("Porównanie:", comparison)

