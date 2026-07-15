import { Construction } from 'lucide-react'

export function MitigateStage() {
  return (
    <div className="rounded-lg bg-bg-2 border border-border-subtle border-dashed px-4 py-8 text-center">
      <Construction className="mx-auto mb-2 text-text-4" size={20} />
      <p className="text-sm text-text-3">Mitigation module not yet implemented.</p>
      <p className="mt-1 text-xs text-text-4">
        Rewriting flagged text into a safer alternative is deliverable #3 — the classifier above is
        real, this stage isn&apos;t wired to a model yet.
      </p>
    </div>
  )
}
