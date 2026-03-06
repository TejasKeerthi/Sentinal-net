/**
 * RiskRadar — Animated radar/spider chart showing 5 risk dimensions.
 * Unique multi-axis risk visualization with rotating sweep line.
 */

interface Props {
  commitRisk: number; // 0-100
  issueRisk: number;
  sentimentRisk: number;
  activityRisk: number;
  complexityRisk: number;
}

const AXES = ['Commits', 'Issues', 'Sentiment', 'Activity', 'Complexity'];
const ANGLE_STEP = (Math.PI * 2) / 5;
const CX = 120;
const CY = 120;
const R = 90;

function polarToCart(angle: number, radius: number) {
  return { x: CX + radius * Math.sin(angle), y: CY - radius * Math.cos(angle) };
}

export const RiskRadar = ({ commitRisk, issueRisk, sentimentRisk, activityRisk, complexityRisk }: Props) => {
  const values = [commitRisk, issueRisk, sentimentRisk, activityRisk, complexityRisk];
  const dataPoints = values.map((v, i) => polarToCart(i * ANGLE_STEP, (v / 100) * R));
  const dataPath = dataPoints.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ') + 'Z';

  // Grid rings
  const rings = [0.25, 0.5, 0.75, 1].map(f =>
    Array.from({ length: 5 }, (_, i) => polarToCart(i * ANGLE_STEP, f * R))
  );

  return (
    <div className="glass-card p-6 anim-fade-up relative overflow-hidden" style={{ animationDelay: '0.4s' }}>
      <h3 className="text-sm font-semibold text-gray-400 tracking-wider uppercase mb-4 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-purple anim-heartbeat" />
        Risk Radar
      </h3>

      <div className="flex justify-center">
        <div className="relative" style={{ width: 240, height: 240 }}>
          {/* Radar sweep animation */}
          <div
            className="absolute inset-0 rounded-full"
            style={{
              background: 'conic-gradient(from 0deg, transparent 0deg, rgba(0,212,255,0.08) 40deg, transparent 80deg)',
              animation: 'radarSweep 5s linear infinite',
            }}
          />
          <svg viewBox="0 0 240 240" width={240} height={240} className="relative z-10">
            <defs>
              <radialGradient id="radarFill">
                <stop offset="0%" stopColor="#00d4ff" stopOpacity="0.25" />
                <stop offset="100%" stopColor="#a855f7" stopOpacity="0.05" />
              </radialGradient>
            </defs>

            {/* Grid */}
            {rings.map((pts, ri) => (
              <polygon
                key={ri}
                points={pts.map(p => `${p.x},${p.y}`).join(' ')}
                fill="none"
                stroke="rgba(255,255,255,0.04)"
                strokeWidth="1"
              />
            ))}

            {/* Axes */}
            {Array.from({ length: 5 }, (_, i) => {
              const end = polarToCart(i * ANGLE_STEP, R);
              return (
                <line key={i} x1={CX} y1={CY} x2={end.x} y2={end.y} stroke="rgba(255,255,255,0.06)" strokeWidth="1" />
              );
            })}

            {/* Data polygon */}
            <polygon points={dataPath.replace(/[MLZ]/g, m => m === 'Z' ? '' : '').replace(/[ML]/g, '')}
              fill="url(#radarFill)" stroke="#00d4ff" strokeWidth="1.5" opacity="0.9"
              style={{ filter: 'drop-shadow(0 0 8px rgba(0,212,255,0.3))' }}
            >
              {/* Pulse */}
              <animate attributeName="opacity" values="0.9;0.6;0.9" dur="3s" repeatCount="indefinite" />
            </polygon>

            {/* Data points */}
            {dataPoints.map((p, i) => (
              <circle key={i} cx={p.x} cy={p.y} r={3.5} fill="#00d4ff" stroke="#fff" strokeWidth="1" opacity="0.9">
                <animate attributeName="r" values="3;5;3" dur={`${2 + i * 0.4}s`} repeatCount="indefinite" />
              </circle>
            ))}

            {/* Labels */}
            {AXES.map((label, i) => {
              const p = polarToCart(i * ANGLE_STEP, R + 18);
              return (
                <text key={i} x={p.x} y={p.y} textAnchor="middle" dominantBaseline="central"
                  fill="#9ca3af" fontSize="9" fontWeight="500">
                  {label}
                </text>
              );
            })}
          </svg>
        </div>
      </div>

      {/* Value pills */}
      <div className="flex flex-wrap justify-center gap-2 mt-4">
        {AXES.map((a, i) => (
          <span key={i} className="px-2 py-1 rounded-full text-[10px] font-semibold bg-white/[0.04] border border-white/[0.06] text-gray-400">
            {a}: <span className={values[i] > 60 ? 'text-danger' : values[i] > 35 ? 'text-warn' : 'text-success'}>{values[i]}%</span>
          </span>
        ))}
      </div>
    </div>
  );
};
