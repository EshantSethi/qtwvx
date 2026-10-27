from datetime import date, datetime, timedelta

import httpx
import pandas as pd

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets"


def _stream(client: httpx.Client, dataset: str, params: dict) -> list[dict]:
    resp = client.get(f"{BASE_URL}/{dataset}/stream", params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()


def fetch_actuals(start: date, end: date) -> pd.DataFrame:
    """Half-hourly wind generation (FUELHH) for start <= settlementDate <= end."""
    with httpx.Client() as client:
        rows = _stream(
            client,
            "FUELHH",
            {
                "settlementDateFrom": start.isoformat(),
                "settlementDateTo": end.isoformat(),
                "fuelType": "WIND",
            },
        )

    df = pd.DataFrame(rows)
    df = df[df["fuelType"] == "WIND"]
    df = df[["startTime", "generation"]].copy()
    df["startTime"] = pd.to_datetime(df["startTime"], utc=True)
    return df.drop_duplicates("startTime").sort_values("startTime").reset_index(drop=True)


def fetch_forecasts(publish_from: datetime, publish_to: datetime, chunk_days: int = 7) -> pd.DataFrame:
    """Hourly wind forecasts (WINDFOR) published between publish_from and publish_to.

    The stream endpoint gets slow on long ranges, so we pull it a week at a time.
    """
    frames = []
    with httpx.Client() as client:
        cur = publish_from
        while cur < publish_to:
            nxt = min(cur + timedelta(days=chunk_days), publish_to)
            rows = _stream(
                client,
                "WINDFOR",
                {
                    "publishDateTimeFrom": cur.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "publishDateTimeTo": nxt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
            )
            if rows:
                frames.append(pd.DataFrame(rows))
            cur = nxt

    df = pd.concat(frames, ignore_index=True)
    df = df[["publishTime", "startTime", "generation"]].copy()
    df["publishTime"] = pd.to_datetime(df["publishTime"], utc=True)
    df["startTime"] = pd.to_datetime(df["startTime"], utc=True)
    df = df.drop_duplicates(["publishTime", "startTime"])
    return df.sort_values(["startTime", "publishTime"]).reset_index(drop=True)
