import pandas as pd
import pytest

from app import analysis


def ts(s):
    return pd.Timestamp(s, tz="UTC")


@pytest.fixture
def forecasts():
    # three forecasts for the same target, published at different times
    return pd.DataFrame(
        {
            "publishTime": [ts("2026-01-09 08:30"), ts("2026-01-09 10:30"), ts("2026-01-09 12:30"), ts("2026-01-10 05:30")],
            "startTime": [ts("2026-01-10 06:00")] * 4,
            "generation": [1000, 1100, 1200, 1300],
        }
    )


def test_day_ahead_uses_last_forecast_before_gate(forecasts):
    chosen = analysis.latest_forecasts(forecasts, analysis.day_ahead_cutoff)
    assert len(chosen) == 1
    # 11:00 on the 9th is the gate, so the 10:30 forecast is the latest usable one
    assert chosen.iloc[0]["generation"] == 1100
    assert chosen.iloc[0]["leadHours"] == pytest.approx(19.5)


def test_horizon_mode(forecasts):
    chosen = analysis.latest_forecasts(forecasts, lambda t: analysis.horizon_cutoff(t, 0))
    assert chosen.iloc[0]["generation"] == 1300

    chosen = analysis.latest_forecasts(forecasts, lambda t: analysis.horizon_cutoff(t, 12))
    assert chosen.iloc[0]["generation"] == 1200

    chosen = analysis.latest_forecasts(forecasts, lambda t: analysis.horizon_cutoff(t, 48))
    assert chosen.empty


def test_error_stats():
    matched = pd.DataFrame(
        {
            "generationForecast": [110, 90, 100, 130],
            "generationActual": [100, 100, 100, 100],
        }
    )
    matched["error"] = matched["generationForecast"] - matched["generationActual"]
    s = analysis.error_stats(matched)

    assert s["points"] == 4
    assert s["mae"] == 12.5
    assert s["bias"] == 7.5
    assert s["shareOverForecast"] == 50.0


def test_match_only_keeps_hourly_points():
    actuals = pd.DataFrame(
        {
            "startTime": [ts("2026-01-10 06:00"), ts("2026-01-10 06:30"), ts("2026-01-10 07:00")],
            "generation": [500, 520, 540],
        }
    )
    chosen = pd.DataFrame(
        {
            "startTime": [ts("2026-01-10 06:00"), ts("2026-01-10 07:00")],
            "publishTime": [ts("2026-01-09 10:30")] * 2,
            "generation": [510, 500],
        }
    )
    m = analysis.match(actuals, chosen)
    assert list(m["error"]) == [10, -40]
