# strategy/gem.py
from strategy.momentum import calculate_all_momentums, fmt_float

REQUIRED_ROLES = {"equity_us", "equity_exus", "defensive"}

def gem_decision(assets: dict) -> dict:
    """
    assets musi zawierać role:
        - equity_us
        - equity_exus
        - defensive

    Zwraca:
        {
            "decisions": dict, # decyzja dla każdego momentum
            "momentums": dict  # wszystkie momentum dla każdego aktywa
        }

    Oblicza momentum 3M, 6M i 12M dla każdego aktywa
    i generuje decyzję GEM dla każdego horyzontu osobno.
    """

    # 🔍 Walidacja ról
    if set(assets.keys()) != REQUIRED_ROLES:
        raise ValueError(
            f"Assets muszą zawierać dokładnie role: {REQUIRED_ROLES}"
        )

    # 📊 Liczymy wszystkie momentum dla każdego aktywa
    momentums = {
        role: calculate_all_momentums(df)
        for role, df in assets.items()
    }

    # 🏆 Decyzje GEM dla każdego horyzontu
    momentum_horizons = list(next(iter(momentums.values())).keys())  # np. ["3M","6M","12M"]
    decisions = {}

    for horizon in momentum_horizons:
        us_mom = momentums["equity_us"][horizon]
        exus_mom = momentums["equity_exus"][horizon]

        if us_mom < 0 and exus_mom < 0:
            decisions[horizon] = "defensive"
        else:
            decisions[horizon] = "equity_us" if us_mom > exus_mom else "equity_exus"

    return {
        "decisions": decisions,
        "momentums": momentums
    }