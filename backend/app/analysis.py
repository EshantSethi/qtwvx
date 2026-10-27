from datetime import timedelta

import numpy as np
import pandas as pd

# GB day-ahead auction closes at 11:00 UK time on the day before delivery.
# In January UK time == UTC, so no DST handling needed for this period.
DAY_AHEAD_GATE_HOUR = 11


def day_ahead_cutoff(targets: pd.Series) -> pd.Series:
    return targets.dt.floor("D") - timedelta(days=1) + timedelta(hours=DAY_AHEAD_GATE_HOUR)


def horizon_cutoff(targets: pd.Series, hours: float) -> pd.Series:
    return targets - timedelta(hours=hours)


def latest_forecasts(forecasts: pd.DataFrame, cutoff_fn) -> pd.DataFrame:
    """For every target time keep the newest forecast published on or before its cutoff."""
    f = forecasts.copy()
    f["cutoff"] = cutoff_fn(f["startTime"])
    f = f[f["publishTime"] <= f["cutoff"]]
    if f.empty:
        return f.drop(columns="cutoff")

    idx = f.groupby("startTime")["publishTime"].idxmax()
    out = f.loc[idx].drop(columns="cutoff").sort_values("startTime").reset_index(drop=True)
    out["leadHours"] = (out["startTime"] - out["publishTime"]).dt.total_seconds() / 3600
    return out


def match(actuals: pd.DataFrame, chosen: pd.DataFrame) -> pd.DataFrame:
    # forecasts are hourly, actuals half-hourly -> compare on the hourly timestamps
    m = chosen.merge(actuals, on="startTime", suffixes=("Forecast", "Actual"))
    m["error"] = m["generationForecast"] - m["generationActual"]
    return m


def error_stats(matched: pd.DataFrame) -> dict:
    if matched.empty:
        return {"points": 0}

    err = matched["error"].to_numpy(dtype=float)
    actual = matched["generationActual"].to_numpy(dtype=float)
    abs_err = np.abs(err)
    mae = abs_err.mean()

    return {
        "points": int(len(err)),
        "mae": round(float(mae), 1),
        "rmse": round(float(np.sqrt((err ** 2).mean())), 1),
        "bias": round(float(err.mean()), 1),
        "p90AbsError": round(float(np.percentile(abs_err, 90)), 1),
        "maxAbsError": round(float(abs_err.max()), 1),
        "maeAsPctOfMeanActual": round(float(mae / actual.mean() * 100), 1),
        # How much to shave off the forecast so wind still turns up at least
        # that much 90% of the time. Positive error = forecast was too high.
        "overForecastP90": round(float(np.percentile(err, 90)), 1),
        "shareOverForecast": round(float((err > 0).mean() * 100), 1),
    }


def horizon_curve(actuals: pd.DataFrame, forecasts: pd.DataFrame, horizons=range(0, 49, 2)) -> list[dict]:
    rows = []
    for h in horizons:
        chosen = latest_forecasts(forecasts, lambda t, h=h: horizon_cutoff(t, h))
        stats = error_stats(match(actuals, chosen))
        if stats["points"] == 0:
            continue
        rows.append(
            {
                "horizon": h,
                "mae": stats["mae"],
                "rmse": stats["rmse"],
                "p90AbsError": stats["p90AbsError"],
                "bias": stats["bias"],
                "points": stats["points"],
            }
        )
    return rows
