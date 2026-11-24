import React from 'react'
import { useAuth } from '../auth/AuthContext'
import { ShieldCheck, Trash2 } from 'lucide-react'

export default function SettingsPage() {
  const { user } = useAuth()

  return (
    <div className="max-w-lg space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Settings</h1>
        <p className="text-slate-400 mt-1">Account and privacy preferences.</p>
      </div>

      <div className="card p-6 space-y-3">
        <h2 className="font-semibold text-slate-100">Account</h2>
        <Row label="Name" value={user?.name} />
        <Row label="Email" value={user?.email} />
      </div>

      <div className="card p-6 space-y-3">
        <div className="flex items-center gap-2 mb-1">
          <ShieldCheck className="text-accent-500" size={18} />
          <h2 className="font-semibold text-slate-100">Privacy & Retention</h2>
        </div>
        <p className="text-sm text-slate-400">
          Files are processed for authenticity analysis and handled according to the configured retention policy.
          By default, uploaded files and analysis results are retained for 30 days before automatic deletion.
        </p>
      </div>

      <div className="card p-6 space-y-3 border-red-500/20">
        <h2 className="font-semibold text-red-400 flex items-center gap-2"><Trash2 size={18} /> Delete My Data</h2>
        <p className="text-sm text-slate-400">
          Permanently delete all uploaded files and analysis history associated with your account.
        </p>
        <button className="btn-secondary border-red-500/40 text-red-400 hover:bg-red-500/10">
          Request Data Deletion
        </button>
      </div>
    </div>
  )
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between text-sm py-1 border-b border-base-700 last:border-0">
      <span className="text-slate-500">{label}</span>
      <span className="text-slate-200">{value}</span>
    </div>
  )
}
