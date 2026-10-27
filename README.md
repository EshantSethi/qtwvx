# UK Wind Forecast Monitor

A small web app for a day-ahead power buying team. It answers two questions:

1. **What wind forecast did we actually have when we had to buy?** For every hour, it shows the latest national wind forecast that was published before the decision point, next to what wind really generated.
2. **How much can we trust it?** It measures the forecast error (MAE, RMSE, bias, 90th-percentile error) and shows how that error grows the further ahead the forecast was made.

Live app: `<vercel link here>`

## Data

Both datasets come from Elexon BMRS:

| Dataset | Used for | Fields |
|---|---|---|
| [FUELHH](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FUELHH/stream) (fuelType = WIND) | actual generation, half-hourly | `startTime`, `generation` |
| [WINDFOR](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/WINDFOR/stream) | forecast generation, hourly | `startTime`, `publishTime`, `generation` |

Scope is January 2026 delivery times. Forecasts are pulled from 29 Dec 2025, so the first days of January still have their day-ahead and 48h-ahead forecasts.

## How the "right" forecast is picked

WINDFOR publishes a new forecast roughly every 3 hours, and each one covers the next ~2.5 days. So every delivery hour has many forecasts for it. The app picks one per hour:

- **Day-ahead mode (default):** GB day-ahead auctions close at 11:00 UK time on the day before delivery. For a delivery hour on day D, we use the newest forecast published at or before 11:00 on D-1. In January, UK time is the same as UTC. In practice this gives lead times of about 14.5 to 37.5 hours.
- **Fixed lead time mode:** use the newest forecast published at least N hours before the delivery hour (N = 0 to 48). This is what drives the lead-time chart.

Forecasts are hourly and actuals are half-hourly, so errors are measured on the hourly timestamps where both exist. Error is `forecast - actual`, so a positive value means wind came in lower than forecast. That is the risky direction for a buyer: they end up short.

## What January 2026 looked like

Day-ahead forecast, all 744 hours of January:

- Mean absolute error: about **2.1 GW**, around 18% of average wind output (~11.6 GW).
- The forecast was **too high in about 84% of hours**, with an average bias of about +1.8 GW.
- Covering 90% of hours would have needed about **4.4 GW** of buffer below the forecast.
- MAE grows from about 1.8 GW for the newest forecast to about 2.4 GW at 48 hours ahead.

The bias stays large even for forecasts made just before delivery, so most of it is probably not weather error. One possible explanation is that FUELHH reports metered output after curtailment (wind farms told to turn down because of grid constraints), while WINDFOR forecasts what the turbines could produce. This needs checking against curtailment data, which is outside this challenge's scope. Either way, the team should not treat the raw forecast as the volume they will get.

## Project layout

```
backend/
  app/
    elexon.py      calls the Elexon stream endpoints
    store.py       downloads January data once, saves CSVs, loads them (cached)
    analysis.py    forecast selection + error statistics
    main.py        FastAPI routes
  data/            actuals.csv, forecasts.csv (created by scripts/fetch_data.py)
  tests/           pytest tests for the analysis logic
  Dockerfile
frontend/
  src/
    App.jsx        page layout + data loading
    api.js         fetch helpers
    components/    Controls, GenerationChart, StatCards, HorizonChart
  Dockerfile, nginx.conf
api/index.py       Vercel serverless entrypoint (wraps the FastAPI app)
scripts/
  fetch_data.py  download the January data into backend/data/
  summary.py     print the headline error numbers
docker-compose.yml
vercel.json
```

### API

| Route | What it returns |
|---|---|
| `GET /api/compare?start&end&mode=dayahead\|horizon&horizon=4` | actual series, chosen forecast series (with publish time and lead hours), error stats |
| `GET /api/horizon-curve?start&end` | MAE / RMSE / P90 / bias for lead times 0 to 48h, in steps of 2 |
| `GET /api/health` | `{ "ok": true }` |

## Running it

**1. Install and (optionally) pre-download the data**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd .. && python scripts/fetch_data.py   # saves backend/data/*.csv
python scripts/summary.py               # prints the January numbers shown above
```

If the CSVs aren't there, the backend downloads them from Elexon on the first request (takes a few seconds) and caches them.

**2a. With Docker**

```bash
docker compose up --build
# app: http://localhost:3000   api: http://localhost:8000/api/health
```

**2b. Without Docker**

```bash
# terminal 1
cd backend && uvicorn app.main:app --reload --port 8000

# terminal 2
cd frontend && npm install && npm run dev
# http://localhost:5173 (Vite proxies /api to :8000)
```

**Tests**

```bash
cd backend && pytest
```

## Deploying (Vercel)

`vercel.json` builds the React app from `frontend/` and serves the FastAPI app as a Python function at `/api/*`. Import the repo in Vercel (no extra settings needed), or run `vercel --prod`.

Committing `backend/data/*.csv` makes the first load faster. Without them the function downloads the month from Elexon into `/tmp` on a cold start.

## Limitations / next steps

- Only national wind is covered. Solar and demand forecasts would give the full net-position picture.
- The large positive bias needs a proper check against curtailment data (e.g. BOALF bid acceptances) before anyone corrects for it.
- The 11:00 gate is hard-coded for winter (UTC = UK time). Summer would need a BST offset.
- Next useful feature: a "buy recommendation" that takes the day-ahead forecast, subtracts a chosen percentile of historical over-forecast error, and shows the volume to cover with firm power.

## Use of AI tools

As the brief allows, I used Claude (Anthropic) as an AI coding assistant on this project. It wrote most of the code and config (FastAPI routes, React components, Docker and Vercel setup) from my prompts.

What I did myself: TODO (Eshant), list only what's true, e.g. "ran it against the live Elexon data and checked the numbers in this README, deployed it to Vercel, reviewed the forecast-selection logic".
