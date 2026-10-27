import { useEffect, useState } from 'react'
import { getCompare, getHorizonCurve } from './api'
import Controls from './components/Controls'
import GenerationChart from './components/GenerationChart'
import StatCards from './components/StatCards'
import HorizonChart from './components/HorizonChart'

const DEFAULTS = {
  start: '2026-01-01T00:00',
  end: '2026-01-08T00:00',
  mode: 'dayahead',
  horizon: 4,
}

// datetime-local gives "2026-01-01T00:00" with no zone; the data is all UTC
const toUtc = (v) => `${v}:00Z`

export default function App() {
  const [filters, setFilters] = useState(DEFAULTS)
  const [data, setData] = useState(null)
  const [curve, setCurve] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const params = {
      start: toUtc(filters.start),
      end: toUtc(filters.end),
      mode: filters.mode,
      horizon: filters.horizon,
    }
    setLoading(true)
    setError('')
    getCompare(params)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [filters])

  useEffect(() => {
    getHorizonCurve({ start: toUtc(filters.start), end: toUtc(filters.end) })
      .then(setCurve)
      .catch(() => setCurve([]))
  }, [filters.start, filters.end])

  return (
    <div className="page">
      <header>
        <h1>UK Wind Forecast Monitor</h1>
        <p className="sub">
          National wind generation vs the forecast you would have had when buying in the day-ahead market.
          Data: Elexon BMRS (FUELHH actuals, WINDFOR forecasts), January 2026, times in UTC.
        </p>
      </header>

      <Controls value={filters} onChange={setFilters} />

      {error && <div className="error">Couldn't load data: {error}</div>}

      <section className="card">
        <div className="card-head">
          <h2>Actual vs forecast</h2>
          {loading && <span className="muted">loading…</span>}
        </div>
        {data && <GenerationChart actual={data.actual} forecast={data.forecast} />}
      </section>

      {data && <StatCards stats={data.stats} mode={filters.mode} horizon={filters.horizon} />}

      <section className="card">
        <h2>How error grows with lead time</h2>
        <p className="muted">
          Average error when you always use the latest forecast published at least N hours before delivery,
          for the selected dates.
        </p>
        <HorizonChart rows={curve} />
      </section>
    </div>
  )
}
