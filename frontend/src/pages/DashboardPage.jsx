import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { UploadCloud, ArrowRight } from 'lucide-react'
import { analysisApi } from '../services/api'
import LabelBadge from '../components/LabelBadge'

export default function DashboardPage() {
  const [recent, setRecent] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    analysisApi.history().then(({ data }) => setRecent(data.history.slice(0, 5))).finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Digital Authenticity Analysis</h1>
        <p className="text-slate-400 mt-1">Upload a file to check its authenticity, or review recent analyses below.</p>
      </div>

      <Link to="/upload" className="card p-8 flex flex-col items-center justify-center text-center hover:border-accent-500/50 transition-colors group">
        <UploadCloud className="text-accent-500 mb-3 group-hover:scale-105 transition-transform" size={36} />
        <span className="font-semibold text-slate-100">Upload File</span>
        <span className="text-sm text-slate-500 mt-1">Images, video, audio, PDF, DOCX</span>
      </Link>

      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-slate-100">Recent Analyses</h2>
          <Link to="/history" className="text-sm text-accent-500 hover:underline flex items-center gap-1">
            View all <ArrowRight size={14} />
          </Link>
        </div>

        {loading ? (
          <p className="text-slate-500 text-sm">Loading…</p>
        ) : recent.length === 0 ? (
          <div className="card p-6 text-center text-slate-500 text-sm">No analyses yet. Upload a file to get started.</div>
        ) : (
          <div className="space-y-2">
            {recent.map((a) => (
              <Link key={a.analysis_id} to={`/results/${a.analysis_id}`}
                className="card p-4 flex items-center justify-between hover:border-accent-500/40 transition-colors">
                <div className="min-w-0">
                  <p className="font-medium text-slate-200 truncate">{a.filename}</p>
                  <p className="text-xs text-slate-500 uppercase">{a.type} · {a.status}</p>
                </div>
                {a.label && <LabelBadge label={a.label} />}
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
