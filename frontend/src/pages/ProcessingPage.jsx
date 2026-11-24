import React, { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Check, Loader2, Circle } from 'lucide-react'
import { analysisApi } from '../services/api'

const STEPS = [
  { key: 'validated', label: 'File validated' },
  { key: 'hashed', label: 'File fingerprint generated' },
  { key: 'processing', label: 'Running forensic analysis' },
  { key: 'completed', label: 'Evidence aggregation & report ready' },
]

export default function ProcessingPage() {
  const { analysisId } = useParams()
  const navigate = useNavigate()
  const [status, setStatus] = useState('QUEUED')
  const [error, setError] = useState('')
  const pollRef = useRef(null)

  useEffect(() => {
    const poll = async () => {
      try {
        const { data } = await analysisApi.status(analysisId)
        setStatus(data.status)
        if (data.status === 'COMPLETED') {
          clearInterval(pollRef.current)
          setTimeout(() => navigate(`/results/${analysisId}`), 600)
        } else if (data.status === 'FAILED') {
          clearInterval(pollRef.current)
          setError(data.error || 'Analysis failed unexpectedly.')
        }
      } catch (e) {
        // transient — keep polling
      }
    }
    poll()
    pollRef.current = setInterval(poll, 1500)
    return () => clearInterval(pollRef.current)
  }, [analysisId, navigate])

  const currentIndex =
    status === 'QUEUED' ? 1 : status === 'PROCESSING' ? 2 : status === 'COMPLETED' ? 4 : 0

  return (
    <div className="max-w-md mx-auto pt-16">
      <h1 className="text-xl font-bold text-slate-100 text-center mb-8">Analyzing your file…</h1>
      <div className="card p-6 space-y-4">
        {STEPS.map((step, i) => {
          const done = i < currentIndex
          const active = i === currentIndex && status !== 'FAILED'
          return (
            <div key={step.key} className="flex items-center gap-3">
              {done ? (
                <Check className="text-emerald-400 shrink-0" size={20} />
              ) : active ? (
                <Loader2 className="text-accent-500 shrink-0 animate-spin" size={20} />
              ) : (
                <Circle className="text-slate-600 shrink-0" size={18} />
              )}
              <span className={done || active ? 'text-slate-200' : 'text-slate-500'}>{step.label}</span>
            </div>
          )
        })}
      </div>

      {error && (
        <div className="card mt-6 p-4 border-red-500/30 text-sm text-red-300">
          The forensic model could not complete analysis. {error}
        </div>
      )}
    </div>
  )
}
