import React from 'react'
import { Link } from 'react-router-dom'
import { ShieldCheck, ImageIcon, Video, AudioLines, FileText, Eye, Lock } from 'lucide-react'

const FEATURES = [
  { icon: ImageIcon, title: 'Image Detection', desc: 'ELA, noise, frequency and copy-move analysis to surface editing artifacts.' },
  { icon: Video, title: 'Video Deepfake Detection', desc: 'Frame-consistency and temporal analysis pipeline, pluggable deepfake models.' },
  { icon: AudioLines, title: 'Audio AI Detection', desc: 'Spectral and consistency analysis of speech and audio recordings.' },
  { icon: FileText, title: 'Document Forensics', desc: 'Metadata, structure, and page-level consistency checks for PDF and DOCX.' },
  { icon: Eye, title: 'Explainable Evidence', desc: 'Every verdict is backed by traceable, individually-scored signals.' },
  { icon: Lock, title: 'Secure Analysis', desc: 'Hashed, validated uploads with configurable retention and access control.' },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-base-950">
      <header className="max-w-6xl mx-auto px-6 py-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck className="text-accent-500" size={26} />
          <span className="font-bold text-lg text-slate-100">TruthLens AI</span>
        </div>
        <div className="flex gap-3">
          <Link to="/login" className="btn-secondary">Login</Link>
          <Link to="/register" className="btn-primary">Get Started</Link>
        </div>
      </header>

      <section className="max-w-4xl mx-auto text-center px-6 pt-20 pb-16">
        <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-50 mb-4">Verify What You See.</h1>
        <p className="text-lg text-slate-400 mb-10">
          AI-powered multimodal digital authenticity analysis for images, videos, audio and documents.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link to="/upload" className="btn-primary text-base px-6 py-3">Analyze a File</Link>
          <Link to="/register" className="btn-secondary text-base px-6 py-3">Create an Account</Link>
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-6 pb-24 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {FEATURES.map(({ icon: Icon, title, desc }) => (
          <div key={title} className="card p-6">
            <Icon className="text-accent-500 mb-3" size={26} />
            <h3 className="font-semibold text-slate-100 mb-1">{title}</h3>
            <p className="text-sm text-slate-400">{desc}</p>
          </div>
        ))}
      </section>

      <footer className="border-t border-base-700 py-8 text-center text-xs text-slate-500">
        Automated digital-authenticity analysis identifies signals associated with manipulation but does not
        constitute definitive proof. Verify independently for high-stakes decisions.
      </footer>
    </div>
  )
}
