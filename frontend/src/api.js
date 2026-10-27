const BASE = import.meta.env.VITE_API_URL || ''

async function get(path, params) {
  const qs = new URLSearchParams(params).toString()
  const res = await fetch(`${BASE}${path}?${qs}`)
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`)
  return res.json()
}

export const getCompare = (params) => get('/api/compare', params)
export const getHorizonCurve = (params) => get('/api/horizon-curve', params)
