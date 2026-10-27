"""Download January 2026 wind actuals + forecasts from Elexon into backend/data/.

Run once before starting the app (or before building the Docker image):
    python scripts/fetch_data.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app import store  # noqa: E402

if __name__ == "__main__":
    store.download()
