/**
 * CodeDNAHelix — A double-helix style visualization that represents
 * the "genetic health" of a repository. Each node is a recent commit,
 * colored by NLP sentiment. Completely unique — no existing tool has this.
 */
import type { SignalItem } from '../types';

interface Props { signals: SignalItem[]; }

export const CodeDNAHelix = ({ signals }: Props) => {
  const nodes = signals.slice(0, 8);
  const h = 320;
  const cx = 100;
  const amp = 35;
  const stepY = h / Math.max(nodes.length + 1, 2);

  const getColor = (s: SignalItem) =>
    s.status === 'Urgent' ? '#ff4d6a' : s.status === 'Negative' ? '#ff8c42' : '#22c55e';

  const points = nodes.map((_, i) => {
    const y = stepY * (i + 1);
    const t = (i / Math.max(nodes.length - 1, 1)) * Math.PI * 2;
    const x1 = cx + Math.sin(t) * amp;
    const x2 = cx - Math.sin(t) * amp;
    return { y, x1, x2 };
  });

  // Build smooth strand paths
  const pathA = points.map((p, i) => (i === 0 ? `M${p.x1},${p.y}` : `L${p.x1},${p.y}`)).join(' ');
  const pathB = points.map((p, i) => (i === 0 ? `M${p.x2},${p.y}` : `L${p.x2},${p.y}`)).join(' ');

  return (
    <div className="glass-card p-6 anim-fade-up" style={{ animationDelay: '0.3s' }}>
      <h3 className="text-sm font-semibold text-gray-400 tracking-wider uppercase mb-4 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-accent anim-heartbeat" />
        Code DNA Helix
      </h3>
      <div className="flex items-center justify-center">
        <svg viewBox={`0 0 200 ${h}`} width={200} height={h} className="dna-glow">
          <defs>
            <linearGradient id="dnaGradA" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#00d4ff" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#a855f7" stopOpacity="0.4" />
            </linearGradient>
            <linearGradient id="dnaGradB" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#a855f7" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#00d4ff" stopOpacity="0.4" />
            </linearGradient>
          </defs>

          {/* Strands */}
          <path d={pathA} fill="none" stroke="url(#dnaGradA)" strokeWidth="2" opacity="0.6" />
          <path d={pathB} fill="none" stroke="url(#dnaGradB)" strokeWidth="2" opacity="0.6" />

          {/* Cross-links + nodes */}
          {points.map((p, i) => (
            <g key={i}>
              <line x1={p.x1} y1={p.y} x2={p.x2} y2={p.y} stroke="rgba(255,255,255,0.06)" strokeWidth="1" />
              <circle cx={p.x1} cy={p.y} r={5} fill={getColor(nodes[i])} opacity="0.9">
                <animate attributeName="r" values="4;6;4" dur={`${2 + i * 0.3}s`} repeatCount="indefinite" />
              </circle>
              <circle cx={p.x2} cy={p.y} r={4} fill={getColor(nodes[i])} opacity="0.5">
                <animate attributeName="r" values="3;5;3" dur={`${2.5 + i * 0.2}s`} repeatCount="indefinite" />
              </circle>
            </g>
          ))}
        </svg>

        {/* Legend */}
        <div className="ml-4 space-y-3 text-xs">
          {nodes.slice(0, 4).map((s, i) => (
            <div key={i} className="flex items-center gap-2 max-w-[140px]">
              <span className="w-2 h-2 rounded-full shrink-0" style={{ background: getColor(s) }} />
              <span className="text-gray-400 truncate">{s.message.slice(0, 30)}</span>
            </div>
          ))}
          <div className="flex items-center gap-3 pt-2 border-t border-white/5">
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-success" /> OK</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-warn" /> Warn</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-danger" /> Bug</span>
          </div>
        </div>
      </div>
    </div>
  );
};
