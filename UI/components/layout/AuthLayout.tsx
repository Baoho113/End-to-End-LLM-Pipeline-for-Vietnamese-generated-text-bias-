import React from 'react'
import { FEATURES } from '@/lib/constants'
import { Eye, BarChart3, Bolt, History, Shield } from 'lucide-react'

interface AuthLayoutProps {
  children: React.ReactNode
}

export const AuthLayout: React.FC<AuthLayoutProps> = ({ children }) => {
  return (
    <div className="w-full h-screen flex bg-[#0a0a0f] font-[Outfit,sans-serif]">
      {/* Sidebar */}
      <div className="hidden md:flex w-70 flex-shrink-0 bg-[#0f0f1a] border-r border-white/[0.07] flex-col p-8 relative overflow-hidden">
        {/* Glow top-left */}
        <div className="pointer-events-none absolute -top-20 -left-20 w-64 h-64 rounded-full bg-[radial-gradient(circle,rgba(99,71,255,0.18)_0%,transparent_70%)]" />
        {/* Glow bottom-right */}
        <div className="pointer-events-none absolute -bottom-16 -right-16 w-52 h-52 rounded-full bg-[radial-gradient(circle,rgba(29,158,117,0.12)_0%,transparent_70%)]" />

        {/* Logo */}
        <div className="flex items-center gap-2.5 mb-8 relative z-10">
          <div className="w-[34px] h-[34px] rounded-[9px] bg-gradient-to-br from-[#6347ff] to-[#9b7dff] flex items-center justify-center flex-shrink-0">
            <Eye size={16} className="text-white" />
          </div>
          <span
            className="text-[18px] text-[#f0eeff] tracking-[-0.3px]"
            style={{ fontFamily: "'DM Serif Display', serif" }}
          >
            BiasLens
          </span>
        </div>

        {/* Tagline */}
        <p
          className="text-[22px] leading-[1.35] text-[#a89fff] mb-7 tracking-[-0.3px] relative z-10"
          style={{ fontFamily: "'DM Serif Display', serif", fontStyle: 'italic' }}
        >
          See what others{' '}
          <span className="text-[#f0eeff] not-italic">miss.</span>
        </p>

        {/* Divider */}
        <div className="h-px bg-white/[0.07] mb-6 relative z-10" />

        {/* Features */}
        <div className="flex flex-col gap-[18px] flex-1 relative z-10">
          {FEATURES.map((feature, idx) => (
            <div key={idx} className="flex items-start gap-3">
              <div className="w-[30px] h-[30px] rounded-lg bg-[rgba(99,71,255,0.12)] border border-[rgba(99,71,255,0.25)] flex items-center justify-center flex-shrink-0 mt-px">
                {feature.icon === 'bolt' && <Bolt size={14} className="text-[#9b7dff]" />}
                {feature.icon === 'shield-lock' && <Shield size={14} className="text-[#9b7dff]" />}
              </div>
              <div className="flex flex-col gap-0.5">
                <span className="text-xs font-medium text-[#d4ccff] tracking-[0.1px]">
                  {feature.title}
                </span>
                <span className="text-[11px] text-white/[0.33] leading-[1.45]">
                  {feature.subtitle}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Stats */}
        <div className="border-t border-white/[0.07] pt-5 flex gap-5 relative z-10">
          {[
            { value: 'Beta', label: 'Early access' },
          ].map((stat) => (
            <div key={stat.label}>
              <div
                className="text-base font-medium text-[#f0eeff] mb-0.5"
                style={{ fontFamily: "'DM Mono', monospace" }}
              >
                {stat.value}
              </div>
              <div className="text-[10px] text-white/30 uppercase tracking-[0.6px]">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Panel */}
      <div className="flex-1 flex items-center justify-center p-10 bg-[#0a0a0f] overflow-y-auto">
        <div className="w-full max-w-[340px]">
          {children}
        </div>
      </div>
    </div>
  )
}