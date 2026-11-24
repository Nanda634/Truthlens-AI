import React from 'react'
import { RadialBarChart, RadialBar, PolarAngleAxis } from 'recharts'

function colorFor(score) {
  if (score <= 20) return '#34d399'
  if (score <= 40) return '#a3e635'
  if (score <= 60) return '#fbbf24'
  if (score <= 80) return '#fb923c'
  return '#f87171'
}

export default function RiskGauge({ score = 0, label = 'Risk Score' }) {
  const color = colorFor(score)
  const data = [{ name: 'risk', value: score, fill: color }]

  return (
    <div className="flex flex-col items-center">
      <RadialBarChart
        width={180}
        height={140}
        cx="50%"
        cy="100%"
        innerRadius={70}
        outerRadius={100}
        startAngle={180}
        endAngle={0}
        data={data}
      >
        <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
        <RadialBar background clockWise dataKey="value" cornerRadius={8} angleAxisId={0} />
      </RadialBarChart>
      <div className="-mt-14 text-center">
        <div className="text-3xl font-extrabold" style={{ color }}>{Math.round(score)}</div>
        <div className="text-xs text-slate-500 mt-1">{label}</div>
      </div>
    </div>
  )
}
