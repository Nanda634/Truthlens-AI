import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Download, FileSearch, ShieldAlert } from 'lucide-react'
import { analysisApi } from '../services/api'
import LabelBadge from '../components/LabelBadge'
import RiskGauge from '../charts/RiskGauge'
import CategoryScoresChart from '../charts/CategoryScoresChart'

export default function ResultPage() {
  const { analysisId } = useParams()
  const [result, setResult] = useState(null)
  const [evidence, setEvidence] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([analysisApi.result(analysisId), analysisApi.evidence(analysisId)])
      .then(([r, e]) => {
        setResult(r.data)
        setEvidence(e.data)
      })
      .catch((err) => setError(err?.response?.data?.detail || 'Unable to load result.'))
  }, [analysisId])

  if (error) {
    return (
      <div className="card p-6 max-w-lg mx-auto flex items-start gap-3 border-red-500/30">
        <ShieldAlert className="text-red-400 shrink-0" size={18} />
        <p className="text-sm text-red-300">{error}</p>
      </div>
    )
  }

  if (!result) return <p className="text-slate-500">Loading result…</p>

  const { file, result: r } = result

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="card p-6 sm:p-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <p className="text-sm text-slate-500 mb-2 truncate">{file.name}</p>
            <LabelBadge label={r.label} size="lg" />
          </div>
          <RiskGauge score={r.risk_score} label={r.risk_label} />
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 pt-6 border-t border-base-700 text-sm">
          <Stat label="Confidence" value={`${Math.round(r.confidence * 100)}%`} />
          <Stat label="Risk Level" value={r.risk_band?.replace('_', ' ')} />
          <Stat label="File Type" value={file.type} small />
          <Stat label="Size" value={`${(file.size / 1024).toFixed(1)} KB`} />
        </div>
      </div>

      <div className="card p-6">
        <h2 className="font-semibold text-slate-100 mb-4">Signal Breakdown</h2>
        <CategoryScoresChart scores={evidence?.category_scores} />
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <Link to={`/evidence/${analysisId}`} className="btn-secondary flex-1 flex items-center justify-center gap-2">
          <FileSearch size={18} /> View Evidence Explorer
        </Link>
        <a href={analysisApi.reportUrl(analysisId)} target="_blank" rel="noreferrer"
          className="btn-primary flex-1 flex items-center justify-center gap-2">
          <Download size={18} /> Download Forensic Report
        </a>
      </div>

      <div className="card p-6">
        <h3 className="text-sm font-semibold text-slate-300 mb-2">What this result does NOT prove</h3>
        <ul className="text-sm text-slate-500 space-y-1 list-disc list-inside">
          {evidence?.limitations?.map((l, i) => <li key={i}>{l}</li>)}
        </ul>
      </div>

      <p className="text-xs text-slate-600 text-center pb-6">{result.disclaimer}</p>
    </div>
  )
}

function Stat({ label, value, small }) {
  return (
    <div>
      <p className="text-slate-500 text-xs mb-1">{label}</p>
      <p className={`font-semibold text-slate-200 ${small ? 'text-xs break-all' : ''}`}>{value ?? '—'}</p>
    </div>
  )
}
