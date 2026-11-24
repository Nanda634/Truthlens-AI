import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const LABELS = {
  metadata: 'Metadata',
  forensic: 'Forensic',
  ml: 'AI Detection',
  structural: 'Structural',
  consistency: 'Consistency',
}

function colorFor(v) {
  if (v == null) return '#334155'
  if (v < 0.3) return '#34d399'
  if (v < 0.55) return '#fbbf24'
  return '#f87171'
}

export default function CategoryScoresChart({ scores = {} }) {
  const data = Object.entries(LABELS).map(([key, label]) => ({
    label,
    value: scores[key] != null ? Math.round(scores[key] * 100) : 0,
    available: scores[key] != null,
  }))

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} layout="vertical" margin={{ left: 10, right: 20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1a2230" horizontal={false} />
        <XAxis type="number" domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 12 }} />
        <YAxis type="category" dataKey="label" width={90} tick={{ fill: '#cbd5e1', fontSize: 13 }} />
        <Tooltip
          contentStyle={{ background: '#111722', border: '1px solid #28334a', borderRadius: 8 }}
          formatter={(v, n, p) => [p.payload.available ? `${v}%` : 'Not available', 'Suspicion score']}
        />
        <Bar dataKey="value" radius={[0, 6, 6, 0]}>
          {data.map((d, i) => (
            <Cell key={i} fill={d.available ? colorFor(d.value / 100) : '#334155'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
