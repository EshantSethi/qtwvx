import { Chart as ChartJS, LineElement, PointElement, LinearScale, Tooltip, Legend } from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(LineElement, PointElement, LinearScale, Tooltip, Legend)

export default function HorizonChart({ rows }) {
  if (!rows.length) return <p className="muted">No data.</p>

  const data = {
    datasets: [
      {
        label: 'Mean absolute error',
        data: rows.map((r) => ({ x: r.horizon, y: r.mae })),
        borderColor: '#ea580c',
        pointRadius: 2,
      },
      {
        label: '90th pct absolute error',
        data: rows.map((r) => ({ x: r.horizon, y: r.p90AbsError })),
        borderColor: '#9333ea',
        borderDash: [4, 4],
        pointRadius: 2,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: { type: 'linear', title: { display: true, text: 'Lead time (hours)' }, min: 0, max: 48 },
      y: { title: { display: true, text: 'MW' }, beginAtZero: true },
    },
  }

  return (
    <div className="chart small">
      <Line data={data} options={options} />
    </div>
  )
}
