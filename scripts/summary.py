"""Print the January 2026 numbers used in the README.

    python scripts/summary.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app import analysis, store  # noqa: E402

actuals, forecasts = store.load()

chosen = analysis.latest_forecasts(forecasts, analysis.day_ahead_cutoff)
stats = analysis.error_stats(analysis.match(actuals, chosen))

print("Day-ahead forecast (D-1 11:00), January 2026")
for k, v in stats.items():
    print(f"  {k:24} {v}")
print(f"  lead time range          {chosen['leadHours'].min()}h - {chosen['leadHours'].max()}h")

print("\nError by lead time")
print(f"  {'hours':>5} {'MAE':>8} {'P90':>8} {'bias':>8}")
for row in analysis.horizon_curve(actuals, forecasts, range(0, 49, 6)):
    print(f"  {row['horizon']:>5} {row['mae']:>8} {row['p90AbsError']:>8} {row['bias']:>8}")
