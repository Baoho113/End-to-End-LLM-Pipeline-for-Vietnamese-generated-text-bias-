'use client'

import clsx from 'clsx'
import { AlertCircle, CheckCircle2, XCircle } from 'lucide-react'
import { DetectionResult } from '@/types'

interface DetectStageProps {
  result: DetectionResult | null
  loading: boolean
  error: string | null
}

function severityOf(pct: number): 'good' | 'warn' | 'bad' {
  if (pct < 33) return 'good'
  if (pct < 66) return 'warn'
  return 'bad'
}

const textClass = { good: 'text-status-green', warn: 'text-status-amber', bad: 'text-status-red' }
const barClass = { good: 'bg-status-green', warn: 'bg-status-amber', bad: 'bg-status-red' }
const pillClass = {
  good: 'bg-status-green bg-opacity-10 border-status-green border-opacity-30 text-status-green',
  warn: 'bg-status-amber bg-opacity-10 border-status-amber border-opacity-30 text-status-amber',
  bad: 'bg-status-red bg-opacity-10 border-status-red border-opacity-30 text-status-red',
}
const icons = { good: CheckCircle2, warn: AlertCircle, bad: XCircle }

export function DetectStage({ result, loading, error }: DetectStageProps) {
  if (loading) {
    return (
      <div className="rounded-lg bg-bg-2 border border-border-subtle px-4 py-8 text-center text-sm text-text-3">
        Analyzing…
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg bg-bg-2 border border-status-red border-opacity-30 px-4 py-4 text-sm text-status-red">
        {error}
      </div>
    )
  }

  if (!result) {
    return (
      <div className="rounded-lg bg-bg-2 border border-border-subtle border-dashed px-4 py-8 text-center text-sm text-text-4">
        Submit a passage above to see category scores here.
      </div>
    )
  }

  const overallPct = Math.round(result.confidence * 100)
  const overallSeverity = severityOf(overallPct)
  const OverallIcon = icons[overallSeverity]

  const sortedProbs = Object.entries(result.probabilities).sort((a, b) => b[1] - a[1])
  const flaggedLabels = new Set(result.labels.map((l) => l.label))

  return (
    <div className="rounded-lg bg-bg-2 border border-border-subtle overflow-hidden">
      <div className="px-4 py-3 border-b border-border">
        <div
          className={clsx(
            'inline-flex items-center gap-2 px-3 py-1.5 rounded-2xl text-sm font-medium border',
            pillClass[overallSeverity],
          )}
        >
          <OverallIcon size={14} />
          <span>
            {result.label} — {overallPct}%
          </span>
        </div>
        {result.labels.length > 1 && (
          <p className="mt-2 text-xs text-text-4">
            Also above threshold:{' '}
            {result.labels
              .slice(1)
              .map((l) => `${l.label} (${Math.round(l.confidence * 100)}%)`)
              .join(', ')}
          </p>
        )}
      </div>

      <div>
        {sortedProbs.map(([label, prob]) => {
          const pct = Math.round(prob * 100)
          const sev = severityOf(pct)
          const flagged = flaggedLabels.has(label)
          return (
            <div
              key={label}
              className={clsx(
                'flex items-center gap-3 px-4 py-2 border-b border-border last:border-none',
                flagged && 'bg-accent bg-opacity-5',
              )}
            >
              <span className="w-52 flex-shrink-0 text-xs text-text-3 truncate">{label}</span>
              <div className="flex-1 h-1.5 bg-bg-3 rounded overflow-hidden">
                <div
                  className={clsx('h-full rounded transition-all duration-500', barClass[sev])}
                  style={{ width: `${pct}%` }}
                />
              </div>
              <span className={clsx('w-10 flex-shrink-0 text-right text-xs font-medium', textClass[sev])}>
                {pct}%
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
