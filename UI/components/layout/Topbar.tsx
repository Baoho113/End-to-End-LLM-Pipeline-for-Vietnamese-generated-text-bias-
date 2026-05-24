import React from 'react'
import { Ghost } from 'lucide-react'

interface TopbarProps {
  ghostMode: boolean
  onToggleGhostMode: () => void
}

export const Topbar: React.FC<TopbarProps> = ({
  ghostMode,
  onToggleGhostMode,
}) => {
  return (
    <div className="h-12 px-3 border-b border-border bg-bg-1/80 backdrop-blur-md flex items-center justify-end">
      <div className="flex items-center gap-3">
        {/* Text */}
        <span
          className="
            text-[11px]
            font-semibold
            tracking-[0.2em]
            uppercase
            text-text-3
            select-none
            transition-all duration-300
            hover:text-text-1
          "
        >
          NEK@NDIDN_CODE
        </span>

        <div className="relative group">
          {/* Tooltip */}
          <div
            className="
              pointer-events-none
              absolute right-0 top-[calc(100%+10px)]
              z-50
              whitespace-nowrap
              rounded-xl
              border border-border-subtle
              bg-bg-2/90
              backdrop-blur-xl
              px-3 py-1.5
              text-[11px]
              font-medium
              text-text-2
              shadow-2xl shadow-black/20

              opacity-0
              translate-y-1
              scale-95

              transition-all duration-200
              ease-[cubic-bezier(0.22,1,0.36,1)]

              group-hover:opacity-100
              group-hover:translate-y-0
              group-hover:scale-100
            "
          >
            {ghostMode
              ? 'Incognito mode enabled'
              : 'Use incognito mode'}
          </div>

          {/* Ghost Button */}
          <button
            type="button"
            aria-label="Toggle incognito mode"
            aria-pressed={ghostMode}
            onClick={onToggleGhostMode}
            className={`
              relative
              group
              flex items-center justify-center
              w-9 h-9
              rounded-xl
              border
              transition-all duration-200
              active:scale-90

              ${
                ghostMode
                  ? `
                    bg-bg-2
                    border-accent
                    text-accent
                    shadow-[0_0_20px_rgba(99,102,241,0.15)]
                  `
                  : `
                    border-transparent
                    text-text-3
                    hover:text-text-1
                    hover:bg-bg-2
                    hover:border-border-subtle
                    hover:shadow-[0_0_20px_rgba(99,102,241,0.08)]
                  `
              }
            `}
          >
            {/* Glow */}
            <div
              className={`
                absolute inset-0 rounded-xl opacity-0 blur-xl transition-opacity duration-300
                ${
                  ghostMode
                    ? 'bg-accent/20 opacity-100'
                    : 'group-hover:opacity-100 bg-white/5'
                }
              `}
            />

            <Ghost
              className={`
                relative z-10
                w-4 h-4
                transition-all duration-200
                ${
                  ghostMode
                    ? 'scale-110'
                    : 'group-hover:scale-110'
                }
              `}
            />
          </button>
        </div>
      </div>
    </div>
  )
}