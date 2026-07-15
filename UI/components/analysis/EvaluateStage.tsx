'use client'

import { EvalMetrics } from '@/types'

interface EvaluateStageProps {
  metrics: EvalMetrics | null
  loading: boolean
}

export function EvaluateStage({ metrics, loading }: EvaluateStageProps) {
  if (loading) {
    return (
      <div className="rounded-lg bg-bg-2 border border-border-subtle px-4 py-8 text-center text-sm text-text-3">
        Loading evaluation metrics…
      </div>
    )
  }

  if (!metrics) {
    return (
      <div className="rounded-lg bg-bg-2 border border-border-subtle border-dashed px-4 py-8 text-center text-sm text-text-4">
        No evaluation snapshot yet — run <code className="text-text-3">python src/training/evaluate.py</code>{' '}
        to generate one.
      </div>
    )
  }

  return (
    <div className="rounded-lg bg-bg-2 border border-border-subtle overflow-hidden">
      <div className="grid grid-cols-4 divide-x divide-border border-b border-border">
        <Cell n={metrics.dataset.train} l="train" />
        <Cell n={metrics.dataset.val} l="val" />
        <Cell n={metrics.dataset.test} l="test" />
        <Cell n={`${Math.round(metrics.overall.macro_f1 * 100)}%`} l="test macro F1" />
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="text-text-4 uppercase tracking-wider">
              <th className="text-left font-medium px-4 py-2">Category</th>
              <th className="text-right font-medium px-4 py-2">Precision</th>
              <th className="text-right font-medium px-4 py-2">Recall</th>
              <th className="text-right font-medium px-4 py-2">F1</th>
              <th className="text-right font-medium px-4 py-2">Support</th>
            </tr>
          </thead>
          <tbody>
            {metrics.per_category.map((c) => (
              <tr key={c.label} className="border-t border-border">
                <td className="px-4 py-2 text-text-2">{c.label}</td>
                <td className="px-4 py-2 text-right text-text-3 tabular-nums">{c.precision.toFixed(2)}</td>
                <td className="px-4 py-2 text-right text-text-3 tabular-nums">{c.recall.toFixed(2)}</td>
                <td className="px-4 py-2 text-right text-text-3 tabular-nums">{c.f1.toFixed(2)}</td>
                <td className="px-4 py-2 text-right text-text-4 tabular-nums">{c.support}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="px-4 py-2 text-[11px] text-text-4 border-t border-border">
        Generated {new Date(metrics.generated_at).toLocaleString()}. Source dataset is
        template-generated with heavy duplication — treat this as a pipeline-correctness check, not a
        production accuracy number (see root README).
      </p>
    </div>
  )
}

function Cell({ n, l }: { n: number | string; l: string }) {
  return (
    <div className="px-4 py-3">
      <div className="text-lg font-semibold text-text-1 tabular-nums">{n}</div>
      <div className="text-[11px] text-text-4">{l}</div>
    </div>
  )
}
