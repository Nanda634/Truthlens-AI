import React, { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Search } from 'lucide-react'
import { analysisApi } from '../services/api'
import LabelBadge from '../components/LabelBadge'

const TYPE_FILTERS = ['all', 'image', 'video', 'audio', 'pdf', 'docx']
const LABEL_FILTERS = ['all', 'AUTHENTIC', 'LIKELY_AUTHENTIC', 'SUSPICIOUS', 'LIKELY_MANIPULATED', 'AI_GENERATED', 'INCONCLUSIVE']

export default function HistoryPage() {
  const [history, setHistory] = useState([])
  const [query, setQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [labelFilter, setLabelFilter] = useState('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    analysisApi.history().then(({ data }) => setHistory(data.history)).finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(() => {
    return history.filter((a) => {
      if (query && !a.filename?.toLowerCase().includes(query.toLowerCase())) return false
      if (typeFilter !== 'all' && a.type !== typeFilter) return false
      if (labelFilter !== 'all' && a.label !== labelFilter) return false
      return true
    })
  }, [history, query, typeFilter, labelFilter])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Analysis History</h1>
        <p className="text-slate-400 mt-1">{history.length} total analyses.</p>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by filename…"
            className="w-full bg-base-900 border border-base-600 rounded-lg pl-9 pr-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-accent-500"
          />
        </div>
        <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}
          className="bg-base-900 border border-base-600 rounded-lg px-3 py-2 text-sm text-slate-200">
          {TYPE_FILTERS.map((t) => <option key={t} value={t}>{t === 'all' ? 'All types' : t.toUpperCase()}</option>)}
        </select>
        <select value={labelFilter} onChange={(e) => setLabelFilter(e.target.value)}
          className="bg-base-900 border border-base-600 rounded-lg px-3 py-2 text-sm text-slate-200">
          {LABEL_FILTERS.map((l) => <option key={l} value={l}>{l === 'all' ? 'All results' : l.replace('_', ' ')}</option>)}
        </select>
      </div>

      {loading ? (
        <p className="text-slate-500 text-sm">Loading…</p>
      ) : filtered.length === 0 ? (
        <div className="card p-6 text-center text-slate-500 text-sm">No analyses match your filters.</div>
      ) : (
        <div className="space-y-2">
          {filtered.map((a) => (
            <Link key={a.analysis_id} to={`/results/${a.analysis_id}`}
              className="card p-4 flex items-center justify-between gap-4 hover:border-accent-500/40 transition-colors">
              <div className="min-w-0 flex-1">
                <p className="font-medium text-slate-200 truncate">{a.filename}</p>
                <p className="text-xs text-slate-500">
                  {new Date(a.started_at).toLocaleDateString()} · {a.type?.toUpperCase()} · {a.status}
                  {a.confidence != null && ` · ${Math.round(a.confidence * 100)}% confidence`}
                </p>
              </div>
              {a.label ? <LabelBadge label={a.label} /> : <span className="text-xs text-slate-500">{a.status}</span>}
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
