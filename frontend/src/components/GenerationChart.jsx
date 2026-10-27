import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Tooltip,
  Legend,
} from 'chart.js'
import 'chartjs-adapter-date-fns'
import { Line } from 'react-chartjs-2'

ChartJS.register(LineElement, PointElement, LinearScale, TimeScale, Tooltip, Legend)

// Chart.js draws dates in the browser's timezone. Shift so the axis shows UTC like the rest of the app.
const utc = (iso) => {
  const d = new Date(iso)
  return d.getTime() + d.getTimezoneOffset() * 60000
}

export default function GenerationChart({ actual, forecast }) {
  const data = {
    datasets: [
      {
        label: 'Actual',
        data: actual.map((d) => ({ x: utc(d.time), y: d.mw })),
        borderColor: '#2563eb',
        borderWidth: 1.5,
        pointRadius: 0,
      },
      {
        label: 'Forecast',
        data: forecast.map((d) => ({ x: utc(d.time), y: d.mw, published: d.published, lead: d.leadHours })),
        borderColor: '#16a34a',
        borderWidth: 1.5,
        pointRadius: 0,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    scales: {
      x: { type: 'time', time: { tooltipFormat: 'dd MMM HH:mm' } },
      y: { title: { display: true, text: 'MW' }, beginAtZero: true },
    },
    plugins: {
      tooltip: {
        callbacks: {
          afterLabel: (ctx) => {
            const raw = ctx.raw
            if (!raw.published) return ''
            return `published ${raw.published.slice(5, 16).replace('T', ' ')} (${raw.lead}h ahead)`
          },
        },
      },
    },
  }

  return (
    <div className="chart">
      <Line data={data} options={options} />
    </div>
  )
}
