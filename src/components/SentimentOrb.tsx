/**
 * SentimentOrb — A unique "mood ring" orb that visualises the overall repo sentiment
 * as a morphing gradient sphere. The colors shift based on NLP sentiment scores.
 * No other tool has anything like this.
 */

interface Props {
  /** Overall sentiment -1 to 1 */
  sentiment: number;
  /** Label like "Overall Positive" */
  label: string;
  /** Number of signals analysed */
  signalCount: number;
}

export const SentimentOrb = ({ sentiment, label, signalCount }: Props) => {
  // Map sentiment to colors
  const hue = Math.round(((sentiment + 1) / 2) * 120); // -1 = 0 (red), 0 = 60 (yellow), 1 = 120 (green)
  const saturation = 75;
  const lightness = 50;
  const primaryColor = `hsl(${hue}, ${saturation}%, ${lightness}%)`;
  const secondaryColor = `hsl(${(hue + 40) % 360}, ${saturation}%, ${lightness - 10}%)`;

  const moodLabel = sentiment > 0.3 ? 'Thriving' : sentiment > 0 ? 'Stable' : sentiment > -0.3 ? 'Stressed' : 'Critical';
  const moodIcon = sentiment > 0.3 ? '✦' : sentiment > 0 ? '◈' : sentiment > -0.3 ? '◇' : '⚠';

  return (
    <div className="glass-card p-6 anim-fade-up flex flex-col items-center text-center" style={{ animationDelay: '0.6s' }}>
      <h3 className="text-sm font-semibold text-gray-400 tracking-wider uppercase mb-5 flex items-center gap-2">
        <span className="text-base">{moodIcon}</span>
        Sentiment Orb
      </h3>

      {/* The Orb */}
      <div className="relative w-32 h-32 mb-5">
        {/* Outer glow */}
        <div
          className="absolute inset-0 rounded-full blur-xl opacity-30"
          style={{
            background: `radial-gradient(circle, ${primaryColor}, transparent 70%)`,
            animation: 'morphBlob 8s ease-in-out infinite',
          }}
        />
        {/* Mid glow */}
        <div
          className="absolute inset-2 rounded-full blur-lg opacity-40"
          style={{
            background: `radial-gradient(circle at 40% 40%, ${secondaryColor}, ${primaryColor})`,
            animation: 'morphBlob 6s ease-in-out infinite reverse',
          }}
        />
        {/* Core sphere */}
        <div
          className="absolute inset-4 rounded-full"
          style={{
            background: `
              radial-gradient(circle at 35% 35%, rgba(255,255,255,0.25) 0%, transparent 50%),
              radial-gradient(circle at 60% 60%, ${secondaryColor}44 0%, transparent 50%),
              linear-gradient(135deg, ${primaryColor}, ${secondaryColor})
            `,
            boxShadow: `
              inset 0 2px 20px rgba(255,255,255,0.15),
              0 0 40px ${primaryColor}55,
              0 0 80px ${primaryColor}22
            `,
            animation: 'float 6s ease-in-out infinite',
          }}
        />
        {/* Glass reflection */}
        <div
          className="absolute rounded-full"
          style={{
            top: '18%',
            left: '22%',
            width: '35%',
            height: '25%',
            background: 'linear-gradient(135deg, rgba(255,255,255,0.3), transparent)',
            borderRadius: '50%',
            filter: 'blur(2px)',
          }}
        />
      </div>

      {/* Mood label */}
      <div className="text-lg font-bold gradient-text mb-1">{moodLabel}</div>
      <div className="text-xs text-gray-500 mb-3">{label}</div>

      {/* Score bar */}
      <div className="w-full max-w-[180px]">
        <div className="flex items-center justify-between text-[10px] text-gray-500 mb-1">
          <span>Negative</span>
          <span>Positive</span>
        </div>
        <div className="h-1.5 bg-white/[0.04] rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-1000"
            style={{
              width: `${((sentiment + 1) / 2) * 100}%`,
              background: `linear-gradient(90deg, #ff4d6a, #ff8c42, #22c55e)`,
              boxShadow: `0 0 8px ${primaryColor}66`,
            }}
          />
        </div>
        <div className="text-[10px] text-gray-500 mt-2">
          Based on <span className="text-accent font-semibold">{signalCount}</span> analysed signals
        </div>
      </div>
    </div>
  );
};
