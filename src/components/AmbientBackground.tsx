/**
 * AmbientBackground — Floating morphing orbs that give the UI
 * a living, breathing atmosphere. Pure CSS, zero JS runtime cost.
 */
export const AmbientBackground = () => (
  <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none" aria-hidden>
    {/* Large blue orb — top-left */}
    <div
      className="absolute -top-[20%] -left-[10%] w-[600px] h-[600px] rounded-full opacity-[0.07] anim-morph"
      style={{ background: 'radial-gradient(circle, #00d4ff 0%, transparent 70%)', animation: 'orbFloat 18s ease-in-out infinite, morphBlob 10s ease-in-out infinite' }}
    />
    {/* Purple orb — center-right */}
    <div
      className="absolute top-[30%] -right-[8%] w-[500px] h-[500px] rounded-full opacity-[0.06]"
      style={{ background: 'radial-gradient(circle, #a855f7 0%, transparent 70%)', animation: 'orbFloat 22s ease-in-out infinite reverse, morphBlob 12s ease-in-out infinite reverse' }}
    />
    {/* Orange orb — bottom-left */}
    <div
      className="absolute -bottom-[15%] left-[20%] w-[450px] h-[450px] rounded-full opacity-[0.05]"
      style={{ background: 'radial-gradient(circle, #ff8c42 0%, transparent 70%)', animation: 'orbFloat 20s ease-in-out infinite 4s, morphBlob 14s ease-in-out infinite' }}
    />
    {/* Dot grid overlay */}
    <div className="absolute inset-0 dot-grid opacity-60" />
    {/* Noise texture */}
    <div className="noise" />
  </div>
);
