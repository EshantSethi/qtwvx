const fmt = (mw) => `${Math.round(mw).toLocaleString()} MW`

export default function StatCards({ stats, mode, horizon }) {
  if (!stats || stats.points === 0) {
    return <section className="card muted">No forecast available for this selection.</section>
  }

  const which = mode === 'dayahead' ? 'the day-ahead forecast' : `forecasts made ${horizon}h+ ahead`
  const direction = stats.bias > 0 ? 'higher' : 'lower'

  return (
    <section className="stats">
      <div className="stat">
        <span className="label">Mean absolute error</span>
        <span className="value">{fmt(stats.mae)}</span>
        <span className="hint">{stats.maeAsPctOfMeanActual}% of average output</span>
      </div>
      <div className="stat">
        <span className="label">Bias</span>
        <span className="value">{stats.bias > 0 ? '+' : ''}{fmt(stats.bias)}</span>
        <span className="hint">forecast above actual {stats.shareOverForecast}% of the time</span>
      </div>
      <div className="stat">
        <span className="label">RMSE</span>
        <span className="value">{fmt(stats.rmse)}</span>
        <span className="hint">worst hour off by {fmt(stats.maxAbsError)}</span>
      </div>
      <div className="stat">
        <span className="label">90th pct over-forecast</span>
        <span className="value">{fmt(Math.max(stats.overForecastP90, 0))}</span>
        <span className="hint">buffer to cover 9 in 10 hours</span>
      </div>

      <p className="takeaway">
        Over {stats.points} hourly points, {which} was off by {fmt(stats.mae)} on average and ran{' '}
        {fmt(Math.abs(stats.bias))} {direction} than what was actually generated. If the team plans on the
        forecast, holding about {fmt(Math.max(stats.overForecastP90, 0))} of extra cover would have been enough in
        90% of hours.
      </p>
    </section>
  )
}
