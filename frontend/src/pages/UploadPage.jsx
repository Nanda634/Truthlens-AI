import React, { useCallback, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { UploadCloud, File as FileIcon, X, ShieldAlert } from 'lucide-react'
import { filesApi, analysisApi } from '../services/api'

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`
}

export default function UploadPage() {
  const navigate = useNavigate()
  const [dragOver, setDragOver] = useState(false)
  const [file, setFile] = useState(null)
  const [uploadInfo, setUploadInfo] = useState(null)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const pickFile = (f) => {
    setError('')
    setUploadInfo(null)
    setFile(f)
  }

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
    if (e.dataTransfer.files?.[0]) pickFile(e.dataTransfer.files[0])
  }, [])

  const doUpload = async () => {
    if (!file) return
    setBusy(true)
    setError('')
    setProgress(0)
    try {
      const { data } = await filesApi.upload(file, setProgress)
      setUploadInfo(data)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Upload failed. Please try a different file.')
    } finally {
      setBusy(false)
    }
  }

  const startAnalysis = async () => {
    if (!uploadInfo) return
    setBusy(true)
    try {
      const { data } = await analysisApi.start(uploadInfo.file_id)
      navigate(`/processing/${data.analysis_id}`)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to start analysis.')
      setBusy(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Upload & Analyze</h1>
        <p className="text-slate-400 mt-1">Supported: images, video, audio, PDF, DOCX.</p>
      </div>

      {!uploadInfo && (
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
          className={`card border-dashed p-10 text-center transition-colors ${dragOver ? 'border-accent-500 bg-accent-500/5' : ''}`}
        >
          <UploadCloud className="mx-auto text-accent-500 mb-3" size={36} />
          <p className="text-slate-300 mb-1">Drag & drop a file here</p>
          <p className="text-slate-500 text-sm mb-4">or</p>
          <label className="btn-secondary inline-block cursor-pointer">
            Browse Files
            <input type="file" className="hidden" onChange={(e) => e.target.files?.[0] && pickFile(e.target.files[0])} />
          </label>

          {file && (
            <div className="mt-6 text-left card p-4 flex items-center justify-between">
              <div className="flex items-center gap-3 min-w-0">
                <FileIcon className="text-accent-500 shrink-0" size={22} />
                <div className="min-w-0">
                  <p className="text-sm font-medium text-slate-200 truncate">{file.name}</p>
                  <p className="text-xs text-slate-500">{formatBytes(file.size)} · {file.type || 'unknown type'}</p>
                </div>
              </div>
              <button onClick={() => setFile(null)} className="text-slate-500 hover:text-slate-300 shrink-0" aria-label="Remove file">
                <X size={18} />
              </button>
            </div>
          )}

          {file && (
            <button onClick={doUpload} disabled={busy} className="btn-primary mt-4 w-full sm:w-auto disabled:opacity-60">
              {busy ? `Uploading… ${progress}%` : 'Upload File'}
            </button>
          )}
        </div>
      )}

      {error && (
        <div className="card p-4 flex items-start gap-3 border-red-500/30">
          <ShieldAlert className="text-red-400 shrink-0" size={18} />
          <p className="text-sm text-red-300">{error}</p>
        </div>
      )}

      {uploadInfo && (
        <div className="card p-6 space-y-3">
          <h2 className="font-semibold text-slate-100 mb-2">File Ready for Analysis</h2>
          <Row label="Filename" value={uploadInfo.filename} />
          <Row label="Type" value={uploadInfo.detected_mime_type} />
          <Row label="Size" value={formatBytes(uploadInfo.size)} />
          <Row label="SHA-256" value={uploadInfo.sha256} mono />
          {uploadInfo.mime_mismatch && (
            <p className="text-xs text-amber-400 bg-amber-500/10 border border-amber-500/30 rounded-lg px-3 py-2">
              Declared file type didn't match its actual signature — analysis will proceed using the detected type.
            </p>
          )}
          <div className="flex gap-3 pt-2">
            <button onClick={startAnalysis} disabled={busy} className="btn-primary flex-1 disabled:opacity-60">
              {busy ? 'Starting…' : 'Start Forensic Analysis'}
            </button>
            <button onClick={() => { setUploadInfo(null); setFile(null) }} className="btn-secondary">Cancel</button>
          </div>
        </div>
      )}
    </div>
  )
}

function Row({ label, value, mono }) {
  return (
    <div className="flex justify-between gap-4 text-sm py-1 border-b border-base-700 last:border-0">
      <span className="text-slate-500 shrink-0">{label}</span>
      <span className={`text-slate-200 text-right break-all ${mono ? 'font-mono text-xs' : ''}`}>{value}</span>
    </div>
  )
}
