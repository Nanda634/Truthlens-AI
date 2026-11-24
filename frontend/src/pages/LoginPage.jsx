import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ShieldCheck } from 'lucide-react'
import { useAuth } from '../auth/AuthContext'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to log in. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-base-950 px-4">
      <div className="w-full max-w-sm">
        <div className="flex items-center gap-2 justify-center mb-8">
          <ShieldCheck className="text-accent-500" size={28} />
          <span className="font-bold text-xl text-slate-100">TruthLens AI</span>
        </div>
        <form onSubmit={submit} className="card p-6 space-y-4">
          <h1 className="text-lg font-semibold text-slate-100">Log in</h1>
          {error && <p className="text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg px-3 py-2">{error}</p>}
          <div>
            <label className="text-sm text-slate-400 mb-1 block" htmlFor="email">Email</label>
            <input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-base-900 border border-base-600 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:border-accent-500" />
          </div>
          <div>
            <label className="text-sm text-slate-400 mb-1 block" htmlFor="password">Password</label>
            <input id="password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-base-900 border border-base-600 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:border-accent-500" />
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full disabled:opacity-60">
            {loading ? 'Logging in…' : 'Log in'}
          </button>
          <p className="text-sm text-slate-500 text-center">
            No account? <Link to="/register" className="text-accent-500 hover:underline">Register</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
