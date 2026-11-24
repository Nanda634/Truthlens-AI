import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, ChevronDown } from 'lucide-react'
import { analysisApi } from '../services/api'

const SEVERITY_CLS = {
  high: 'text-red-400 bg-red-500/10 border-red-500/30',
  medium: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
  low: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
}

export default function EvidencePage() {
  const { analysisId } = useParams()
  const [evidence, setEvidence] = useState(null)
  const [openIdx, setOpenIdx] = useState(null)

  useEffect(() => {
    analysisApi.evidence(analysisId).then(({ data }) => setEvidence(data))
  }, [analysisId])

  if (!evidence) return <p className="text-slate-500">Loading evidence…</p>

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <Link to={`/results/${analysisId}`} className="text-sm text-slate-400 hover:text-slate-200 flex items-center gap-1">
        <ArrowLeft size={16} /> Back to result
      </Link>

      <div>
        <h1 className="text-2xl font-bold text-slate-100">Evidence Explorer</h1>
        <p className="text-slate-400 mt-1">Every signal that contributed to the final assessment, individually scored.</p>
      </div>

      <div className="space-y-3">
        {evidence.signals.map((s, i) => (
          <div key={i} className="card overflow-hidden">
            <button
              onClick={() => setOpenIdx(openIdx === i ? null : i)}
              className="w-full flex items-center justify-between p-4 text-left"
            >
              <div className="min-w-0">
                <p className="text-xs text-slate-500 uppercase">{s.type}</p>
                <p className="font-medium text-slate-200">{s.name}</p>
              </div>
              <div className="flex items-center gap-3 shrink-0">
                {s.severity && (
                  <span className={`text-xs px-2 py-1 rounded-md border capitalize ${SEVERITY_CLS[s.severity] || ''}`}>
                    {s.severity}
                  </span>
                )}
                {s.score != null && <span className="text-sm text-slate-400 font-mono">{Math.round(s.score * 100)}%</span>}
                <ChevronDown size={16} className={`text-slate-500 transition-transform ${openIdx === i ? 'rotate-180' : ''}`} />
              </div>
            </button>
            {openIdx === i && (
              <div className="px-4 pb-4 text-sm text-slate-400 border-t border-base-700 pt-3">
                {s.description}
              </div>
            )}
          </div>
        ))}
      </div>

      {evidence.regions?.length > 0 && (
        <div className="card p-4">
          <h2 className="font-semibold text-slate-100 mb-3">Detected Regions</h2>
          <div className="space-y-2 text-sm text-slate-400">
            {evidence.regions.map((r, i) => (
              <div key={i} className="flex justify-between border-b border-base-700 last:border-0 py-1">
                <span>
                  {r.page_number != null && `Page ${r.page_number}`}
                  {r.frame_number != null && `Frame ${r.frame_number}`}
                  {r.x != null && ` @ (${Math.round(r.x)}, ${Math.round(r.y)})`}
                </span>
                <span>{r.confidence != null ? `${Math.round(r.confidence * 100)}% confidence` : ''}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card p-4">
        <h2 className="font-semibold text-slate-100 mb-2">Limitations</h2>
        <ul className="text-sm text-slate-500 space-y-1 list-disc list-inside">
          {evidence.limitations.map((l, i) => <li key={i}>{l}</li>)}
        </ul>
      </div>
    </div>
  )
}
