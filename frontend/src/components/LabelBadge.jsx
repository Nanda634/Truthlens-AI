import React from 'react'
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle, Ban } from 'lucide-react'

const CONFIG = {
  AUTHENTIC: { cls: 'label-authentic', icon: CheckCircle2, text: 'Authentic' },
  LIKELY_AUTHENTIC: { cls: 'label-authentic', icon: CheckCircle2, text: 'Likely Authentic' },
  SUSPICIOUS: { cls: 'label-suspicious', icon: AlertTriangle, text: 'Suspicious' },
  INCONCLUSIVE: { cls: 'label-suspicious', icon: HelpCircle, text: 'Inconclusive' },
  LIKELY_MANIPULATED: { cls: 'label-manipulated', icon: XCircle, text: 'Likely Manipulated' },
  AI_GENERATED: { cls: 'label-manipulated', icon: XCircle, text: 'AI Generated' },
  LIKELY_AI_GENERATED: { cls: 'label-manipulated', icon: XCircle, text: 'Likely AI Generated' },
  TAMPERED: { cls: 'label-manipulated', icon: XCircle, text: 'Tampered' },
  UNSUPPORTED: { cls: 'label-suspicious', icon: Ban, text: 'Unsupported' },
}

export default function LabelBadge({ label, size = 'md' }) {
  const conf = CONFIG[label] || CONFIG.INCONCLUSIVE
  const Icon = conf.icon
  const sizeCls = size === 'lg' ? 'text-2xl px-5 py-3 gap-3' : 'text-sm px-3 py-1.5 gap-2'
  const iconSize = size === 'lg' ? 28 : 16

  return (
    <span className={`inline-flex items-center rounded-lg border font-bold ${conf.cls} ${sizeCls}`}>
      <Icon size={iconSize} />
      {conf.text}
    </span>
  )
}
