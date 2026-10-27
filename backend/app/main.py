from datetime import datetime
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from . import analysis, store

app = FastAPI(title="Wind forecast monitor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def _window(start: datetime | None, end: datetime | None):
    actuals, forecasts = store.load()
    lo = start or store.PERIOD_START
    hi = end or store.PERIOD_END
    if lo.tzinfo is None:
        lo = lo.replace(tzinfo=store.PERIOD_START.tzinfo)
    if hi.tzinfo is None:
        hi = hi.replace(tzinfo=store.PERIOD_START.tzinfo)
    if lo >= hi:
        raise HTTPException(400, "start must be before end")

    a = actuals[(actuals["startTime"] >= lo) & (actuals["startTime"] < hi)]
    f = forecasts[(forecasts["startTime"] >= lo) & (forecasts["startTime"] < hi)]
    return a, f


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/range")
def data_range():
    return {"start": store.PERIOD_START.isoformat(), "end": store.PERIOD_END.isoformat()}


@app.get("/api/compare")
def compare(
    start: datetime | None = None,
    end: datetime | None = None,
    mode: Literal["dayahead", "horizon"] = "dayahead",
    horizon: float = Query(4, ge=0, le=48),
):
    actuals, forecasts = _window(start, end)

    if mode == "dayahead":
        chosen = analysis.latest_forecasts(forecasts, analysis.day_ahead_cutoff)
    else:
        chosen = analysis.latest_forecasts(forecasts, lambda t: analysis.horizon_cutoff(t, horizon))

    matched = analysis.match(actuals, chosen)

    return {
        "actual": [
            {"time": t.isoformat(), "mw": int(g)}
            for t, g in zip(actuals["startTime"], actuals["generation"])
        ],
        "forecast": [
            {"time": t.isoformat(), "mw": int(g), "published": p.isoformat(), "leadHours": round(lh, 1)}
            for t, g, p, lh in zip(chosen["startTime"], chosen["generation"], chosen["publishTime"], chosen.get("leadHours", []))
        ],
        "stats": analysis.error_stats(matched),
    }


@app.get("/api/horizon-curve")
def horizon_curve(start: datetime | None = None, end: datetime | None = None):
    actuals, forecasts = _window(start, end)
    return analysis.horizon_curve(actuals, forecasts)
