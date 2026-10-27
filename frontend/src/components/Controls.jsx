const MIN = '2026-01-01T00:00'
const MAX = '2026-02-01T00:00'

export default function Controls({ value, onChange }) {
  const set = (key) => (e) => onChange({ ...value, [key]: e.target.value })

  return (
    <section className="card controls">
      <label>
        From
        <input type="datetime-local" min={MIN} max={MAX} value={value.start} onChange={set('start')} />
      </label>
      <label>
        To
        <input type="datetime-local" min={MIN} max={MAX} value={value.end} onChange={set('end')} />
      </label>

      <div className="mode">
        <span>Forecast used</span>
        <div className="toggle">
          <button
            className={value.mode === 'dayahead' ? 'on' : ''}
            onClick={() => onChange({ ...value, mode: 'dayahead' })}
          >
            Day-ahead (D-1 11:00)
          </button>
          <button
            className={value.mode === 'horizon' ? 'on' : ''}
            onClick={() => onChange({ ...value, mode: 'horizon' })}
          >
            Fixed lead time
          </button>
        </div>
      </div>

      {value.mode === 'horizon' && (
        <label className="slider">
          At least {value.horizon}h before delivery
          <input
            type="range"
            min="0"
            max="48"
            step="1"
            value={value.horizon}
            onChange={(e) => onChange({ ...value, horizon: Number(e.target.value) })}
          />
        </label>
      )}
    </section>
  )
}
