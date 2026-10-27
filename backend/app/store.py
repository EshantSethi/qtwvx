from datetime import date, datetime, timezone
from functools import lru_cache
from pathlib import Path

import pandas as pd

from . import elexon

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ACTUALS_FILE = DATA_DIR / "actuals.csv"
FORECASTS_FILE = DATA_DIR / "forecasts.csv"

# Scope from the brief: purchase decisions made in January 2026.
# We look at delivery times through January, and pull forecasts from a few
# days earlier so 1 Jan still has its day-ahead and 48h-ahead forecasts.
PERIOD_START = datetime(2026, 1, 1, tzinfo=timezone.utc)
PERIOD_END = datetime(2026, 2, 1, tzinfo=timezone.utc)
FORECAST_PUBLISH_FROM = datetime(2025, 12, 29, tzinfo=timezone.utc)


def download() -> None:
    DATA_DIR.mkdir(exist_ok=True)

    actuals = elexon.fetch_actuals(date(2025, 12, 31), date(2026, 2, 1))
    actuals = actuals[(actuals["startTime"] >= PERIOD_START) & (actuals["startTime"] < PERIOD_END)]
    actuals.to_csv(ACTUALS_FILE, index=False)

    forecasts = elexon.fetch_forecasts(FORECAST_PUBLISH_FROM, PERIOD_END)
    forecasts = forecasts[(forecasts["startTime"] >= PERIOD_START) & (forecasts["startTime"] < PERIOD_END)]
    # forecasts for times already in the past aren't useful for a buying decision
    forecasts = forecasts[forecasts["startTime"] >= forecasts["publishTime"]]
    forecasts.to_csv(FORECASTS_FILE, index=False)

    print(f"saved {len(actuals)} actual rows, {len(forecasts)} forecast rows to {DATA_DIR}")


@lru_cache(maxsize=1)
def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not (ACTUALS_FILE.exists() and FORECASTS_FILE.exists()):
        download()

    actuals = pd.read_csv(ACTUALS_FILE, parse_dates=["startTime"])
    forecasts = pd.read_csv(FORECASTS_FILE, parse_dates=["publishTime", "startTime"])
    return actuals, forecasts
