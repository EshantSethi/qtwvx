import pandas as pd

from app import store


def fake_actuals(start, end):
    t = pd.date_range("2026-01-01", periods=4, freq="30min", tz="UTC")
    return pd.DataFrame({"startTime": t, "generation": [1, 2, 3, 4]})


def fake_forecasts(publish_from, publish_to):
    return pd.DataFrame(
        {
            "publishTime": pd.to_datetime(["2025-12-31 10:30"] * 2, utc=True),
            "startTime": pd.to_datetime(["2026-01-01 00:00", "2026-01-01 01:00"], utc=True),
            "generation": [5, 6],
        }
    )


def test_load_downloads_when_no_data(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "BUNDLED_DIR", tmp_path / "bundled")
    monkeypatch.setattr(store, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(store.elexon, "fetch_actuals", fake_actuals)
    monkeypatch.setattr(store.elexon, "fetch_forecasts", fake_forecasts)
    store.load.cache_clear()

    actuals, forecasts = store.load()

    assert len(actuals) == 4
    assert len(forecasts) == 2
    assert (tmp_path / "bundled" / "actuals.csv").exists()
    store.load.cache_clear()
