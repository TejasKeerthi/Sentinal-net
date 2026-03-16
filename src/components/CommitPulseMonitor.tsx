/**
 * CommitPulseMonitor — Heart-rate / ECG style monitor showing commit frequency
 * as a live-looking pulse line. Truly unique — no other app shows git commits as a heartbeat.
 */

import { useMemo } from 'react';

interface Props {
  /** Array of recent commit timestamps (ISO strings or Date objects) */
  timestamps: string[];
  /** Overall risk 0-100 — affects pulse color */
  risk: number;
}

export const CommitPulseMonitor = ({ timestamps, risk }: Props) => {
  // Build pulse data: group commits by "hour buckets" (last 24h)
  const pulseData = useMemo(() => {
    const now = timestamps.length
      ? Math.max(...timestamps.map((t) => new Date(t).getTime()))
      : 0;
    const buckets = Array.from({ length: 24 }, () => 0);
    timestamps.forEach(t => {
      const hoursAgo = Math.floor((now - new Date(t).getTime()) / 3_600_000);
      if (hoursAgo >= 0 && hoursAgo < 24) buckets[23 - hoursAgo]++;
    });
    return buckets;
  }, [timestamps]);

  const max = Math.max(...pulseData, 1);

  // Generate ECG-style path
  const W = 480;
  const H = 80;
  const stepX = W / (pulseData.length - 1);

  const pathD = pulseData.map((v, i) => {
    const x = i * stepX;
    const normalised = v / max;
    // ECG spike shape: flat → spike → flat
    const baseY = H * 0.7;
    const spikeH = normalised * H * 0.6;
    if (normalised > 0.1) {
      const x0 = x - stepX * 0.15;
      const x1 = x;
      const x2 = x + stepX * 0.15;
      return `L${x0},${baseY} L${x1},${baseY - spikeH} L${x2},${baseY}`;
    }
    return `L${x},${baseY}`;
  }).join(' ');

  const fullPath = `M0,${H * 0.7} ${pathD}`;

  const pulseColor = risk > 60 ? '#ff4d6a' : risk > 35 ? '#ff8c42' : '#00d4ff';
  const pulseGlow = risk > 60 ? 'rgba(255,77,106,0.4)' : risk > 35 ? 'rgba(255,140,66,0.3)' : 'rgba(0,212,255,0.3)';
  const bpm = Math.max(timestamps.length, 1);

  return (
    <div className="glass-card p-6 anim-fade-up relative overflow-hidden" style={{ animationDelay: '0.5s' }}>
      {/* Scan line */}
      <div
        className="absolute top-0 left-0 h-full w-[2px] opacity-50"
        style={{
          background: `linear-gradient(to bottom, transparent, ${pulseColor}, transparent)`,
          animation: 'shimmer 3s ease-in-out infinite',
        }}
      />

      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-400 tracking-wider uppercase flex items-center gap-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="absolute inline-flex h-full w-full rounded-full opacity-75 anim-heartbeat" style={{ backgroundColor: pulseColor }} />
            <span className="relative inline-flex rounded-full h-2.5 w-2.5" style={{ backgroundColor: pulseColor }} />
          </span>
          Commit Pulse
        </h3>
        <span className="text-xs font-mono" style={{ color: pulseColor }}>
          {bpm} commits / 24h
        </span>
      </div>

      <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-20" preserveAspectRatio="none">
        <defs>
          <linearGradient id="pulseFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={pulseColor} stopOpacity="0.15" />
            <stop offset="100%" stopColor={pulseColor} stopOpacity="0" />
          </linearGradient>
          <filter id="pulseGlow">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Grid lines */}
        {[0.25, 0.5, 0.75].map(f => (
          <line key={f} x1={0} y1={H * f} x2={W} y2={H * f} stroke="rgba(255,255,255,0.03)" strokeWidth="0.5" />
        ))}

        {/* Fill area */}
        <path d={`${fullPath} L${W},${H} L0,${H} Z`} fill="url(#pulseFill)" />

        {/* Pulse line */}
        <path d={fullPath} fill="none" stroke={pulseColor} strokeWidth="2" filter="url(#pulseGlow)"
          strokeLinecap="round" strokeLinejoin="round" opacity="0.9"
        />

        {/* Moving dot at end */}
        <circle cx={W} cy={H * 0.7} r="4" fill={pulseColor}>
          <animate attributeName="opacity" values="1;0.3;1" dur="1.5s" repeatCount="indefinite" />
          <animate attributeName="r" values="3;5;3" dur="1.5s" repeatCount="indefinite" />
        </circle>
      </svg>

      {/* Footer stats */}
      <div className="flex items-center justify-between mt-3 text-[11px] text-gray-500">
        <span>24h commit frequency</span>
        <span className="px-2 py-0.5 rounded-full font-semibold border"
          style={{
            color: pulseColor,
            borderColor: `${pulseColor}33`,
            backgroundColor: `${pulseColor}0a`,
            boxShadow: `0 0 12px ${pulseGlow}`,
          }}>
          {risk > 60 ? 'CRITICAL' : risk > 35 ? 'ELEVATED' : 'HEALTHY'}
        </span>
      </div>
    </div>
  );
};
