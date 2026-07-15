import React from 'react'
import { BiasAnalysisResult } from '@/types'
import { calculateAverageScore, formatScore } from '@/lib/utils'
import { CheckCircle2, AlertCircle, XCircle, BarChart3 } from 'lucide-react'
import clsx from 'clsx'

interface BiasCardProps {
  data: BiasAnalysisResult
}

export const BiasCard: React.FC<BiasCardProps> = ({ data }) => {
  const avgScore = calculateAverageScore(data.biases.map(b => b.score))

  const getBarColor = (score: number) => {
    if (score < 33) return 'bg-status-green'
    if (score < 66) return 'bg-status-amber'
    return 'bg-status-red'
  }

  const getScoreColor = (score: number) => {
    if (score < 33) return 'text-status-green'
    if (score < 66) return 'text-status-amber'
    return 'text-status-red'
  }

  const getBadgeColor = () => {
    if (data.overall === 'low') return 'bg-status-green bg-opacity-12 border-status-green border-opacity-20 text-status-green'
    if (data.overall === 'medium') return 'bg-status-amber bg-opacity-12 border-status-amber border-opacity-20 text-status-amber'
    return 'bg-status-red bg-opacity-12 border-status-red border-opacity-20 text-status-red'
  }

  const getBadgeIcon = () => {
    if (data.overall === 'low') return <CheckCircle2 size={14} />
    if (data.overall === 'medium') return <AlertCircle size={14} />
    return <XCircle size={14} />
  }

  return (
    <div className="mt-2 rounded-lg bg-bg-2 border border-border overflow-hidden w-full">
      <div className="px-3 py-2 bg-bg-3 border-b border-border flex items-center justify-between text-text-3">
        <div className="flex items-center gap-1 text-xs font-medium uppercase tracking-wider">
          <BarChart3 size={14} />
          <span>Bias breakdown</span>
        </div>
        <span className="text-xs text-text-4">avg {avgScore}%</span>
      </div>

      {data.biases.map(bias => {
        const score = formatScore(bias.score)
        return (
          <div
            key={bias.type}
            className="px-3 py-2 border-b border-opacity-5 border-white last:border-none flex items-center gap-2"
          >
            <span className="text-xs text-text-3 w-20 flex-shrink-0">{bias.type}</span>
            <div className="flex-1 h-1 bg-white bg-opacity-10 rounded overflow-hidden">
              <div
                className={clsx('h-full rounded transition-all duration-600', getBarColor(score))}
                style={{ width: `${score}%` }}
              />
            </div>
            <span className={clsx('text-xs font-medium w-8 text-right flex-shrink-0', getScoreColor(score))}>
              {score}%
            </span>
            {bias.note && (
              <span className="text-xs text-text-4 flex-1 whitespace-nowrap overflow-hidden text-ellipsis max-w-xs" title={bias.note}>
                {bias.note}
              </span>
            )}
          </div>
        )
      })}

      <div className={clsx('inline-flex items-center gap-2 px-3 py-2 rounded-2xl text-sm font-medium mt-2 mx-3 mb-3 border', getBadgeColor())}>
        <span>{getBadgeIcon()}</span>
        <span>Overall: {data.overall} bias</span>
      </div>
    </div>
  )
}
