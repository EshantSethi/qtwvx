import os
import tempfile
from datetime import date, datetime, timezone
from functools import lru_cache
from pathlib import Path

import pandas as pd

from . import elexon

BUNDLED_DIR = Path(__file__).resolve().parent.parent / "data"
# serverless hosts (Vercel) have a read-only code dir, so fall back to /tmp
CACHE_DIR = Path(os.environ.get("DATA_CACHE_DIR", tempfile.gettempdir())) / "wind-monitor"

# Scope from the brief: purchase decisions made in January 2026.
# We look at delivery times through January, and pull forecasts from a few
# days earlier so 1 Jan still has its day-ahead and 48h-ahead forecasts.
PERIOD_START = datetime(2026, 1, 1, tzinfo=timezone.utc)
PERIOD_END = datetime(2026, 2, 1, tzinfo=timezone.utc)
FORECAST_PUBLISH_FROM = datetime(2025, 12, 29, tzinfo=timezone.utc)


def _files(folder: Path) -> tuple[Path, Path]:
    return folder / "actuals.csv", folder / "forecasts.csv"


def download(folder: Path = BUNDLED_DIR) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    actuals_file, forecasts_file = _files(folder)

    actuals = elexon.fetch_actuals(date(2025, 12, 31), date(2026, 2, 1))
    actuals = actuals[(actuals["startTime"] >= PERIOD_START) & (actuals["startTime"] < PERIOD_END)]
    actuals.to_csv(actuals_file, index=False)

    forecasts = elexon.fetch_forecasts(FORECAST_PUBLISH_FROM, PERIOD_END)
    forecasts = forecasts[(forecasts["startTime"] >= PERIOD_START) & (forecasts["startTime"] < PERIOD_END)]
    # forecasts for times already in the past aren't useful for a buying decision
    forecasts = forecasts[forecasts["startTime"] >= forecasts["publishTime"]]
    forecasts.to_csv(forecasts_file, index=False)

    print(f"saved {len(actuals)} actual rows, {len(forecasts)} forecast rows to {folder}")


def _data_folder() -> Path:
    for folder in (BUNDLED_DIR, CACHE_DIR):
        if all(f.exists() for f in _files(folder)):
            return folder

    try:
        download(BUNDLED_DIR)
        return BUNDLED_DIR
    except OSError:
        download(CACHE_DIR)
        return CACHE_DIR


@lru_cache(maxsize=1)
def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    actuals_file, forecasts_file = _files(_data_folder())
    actuals = pd.read_csv(actuals_file, parse_dates=["startTime"])
    forecasts = pd.read_csv(forecasts_file, parse_dates=["publishTime", "startTime"])
    return actuals, forecasts
