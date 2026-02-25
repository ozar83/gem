from dateutil.relativedelta import relativedelta
import pandas as pd

def calculate_required_start_date(decision_start_date, momentum_window):
    """
    Wyznacza minimalną datę początkową danych potrzebnych
    do rozpoczęcia inwestowania w decision_start_date.
    """
    decision_start_date = pd.to_datetime(decision_start_date)
    required_start = decision_start_date - relativedelta(months=momentum_window + 1)
    return required_start

