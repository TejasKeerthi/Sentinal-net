import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp } from 'lucide-react';
import type { TemporalDataPoint } from '../types';

interface TemporalChartProps {
  data: TemporalDataPoint[];
}

export const TemporalChart = ({ data }: TemporalChartProps) => {
  const avgBugGrowth = data.length > 0 ? Math.round(data.reduce((sum, d) => sum + d.bugGrowth, 0) / data.length) : 0;
  const avgDevIrregularity = data.length > 0 ? Math.round(data.reduce((sum, d) => sum + d.devIrregularity, 0) / data.length) : 0;

  return (
    <div className="glass-card p-6 anim-fade-up relative overflow-hidden" style={{ animationDelay: '0.15s' }}>
      {/* Ambient glow */}
      <div className="absolute -top-16 -right-16 w-40 h-40 rounded-full opacity-10 blur-3xl pointer-events-none"
        style={{ background: 'radial-gradient(circle, #ff8c42, transparent 70%)' }} />

      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-3">
            <div className="p-2 rounded-xl glass" style={{ boxShadow: '0 0 16px rgba(255,140,66,0.12)' }}>
              <TrendingUp size={20} className="text-warn" />
            </div>
            Temporal Trends
          </h2>
          <p className="text-gray-600 text-xs mt-1 ml-12">24-hour trend visualization with ML insights</p>
        </div>
      </div>

      <div className="w-full h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
            <defs>
              <linearGradient id="bugGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ff8c42" stopOpacity={0.6} />
                <stop offset="95%" stopColor="#ff8c42" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="devGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.6} />
                <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
              </linearGradient>
              <filter id="glow">
                <feGaussianBlur stdDeviation="2" result="coloredBlur" />
                <feMerge>
                  <feMergeNode in="coloredBlur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>
            
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
            <XAxis dataKey="timestamp" stroke="#333" tick={{ fill: '#555', fontSize: 11 }} axisLine={{ stroke: 'rgba(255,255,255,0.04)' }} />
            <YAxis stroke="#333" tick={{ fill: '#555', fontSize: 11 }} axisLine={{ stroke: 'rgba(255,255,255,0.04)' }} />
            
            <Tooltip
              contentStyle={{
                background: 'rgba(10,10,20,0.9)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(0,212,255,0.15)',
                borderRadius: '12px',
                boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
              }}
              labelStyle={{ color: '#00d4ff', fontWeight: 600, fontSize: 12 }}
              formatter={(value: number) => [`${value}%`]}
              cursor={{ stroke: 'rgba(0,212,255,0.1)' }}
            />
            
            <Legend
              wrapperStyle={{ fontSize: '11px', color: '#666', paddingTop: '16px' }}
              formatter={(value: string) => {
                if (value === 'bugGrowth') return 'Bug Growth Rate';
                if (value === 'devIrregularity') return 'Dev Irregularity';
                return value;
              }}
              verticalAlign="bottom"
              height={36}
            />
            
            <Line type="monotone" dataKey="bugGrowth" stroke="#ff8c42" fill="url(#bugGradient)" name="bugGrowth"
              strokeWidth={2.5} dot={{ fill: '#ff8c42', r: 4, strokeWidth: 0 }}
              activeDot={{ r: 7, fill: '#ff8c42', filter: 'url(#glow)' }}
              isAnimationActive={true} animationDuration={800} />
            
            <Line type="monotone" dataKey="devIrregularity" stroke="#00d4ff" fill="url(#devGradient)" name="devIrregularity"
              strokeWidth={2.5} dot={{ fill: '#00d4ff', r: 4, strokeWidth: 0 }}
              activeDot={{ r: 7, fill: '#00d4ff', filter: 'url(#glow)' }}
              isAnimationActive={true} animationDuration={800} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Metric pills */}
      <div className="mt-5 grid grid-cols-2 gap-3">
        <div className="glass p-4 rounded-xl">
          <div className="text-warn text-[11px] font-semibold mb-1">Bug Growth Avg</div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-xl font-bold text-warn">{avgBugGrowth}</span>
            <span className="text-[10px] text-gray-600">% avg</span>
          </div>
        </div>
        <div className="glass p-4 rounded-xl">
          <div className="text-accent text-[11px] font-semibold mb-1">Dev Irregularity Avg</div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-xl font-bold text-accent">{avgDevIrregularity}</span>
            <span className="text-[10px] text-gray-600">% avg</span>
          </div>
        </div>
      </div>

      {/* Insight */}
      <div className="mt-4 p-3 glass rounded-xl text-gray-400 text-xs leading-relaxed">
        <span className="text-accent font-semibold">Analysis:</span> {avgBugGrowth > 30 ? 'High' : 'Moderate'} bug growth with {avgDevIrregularity > 20 ? 'significant' : 'moderate'} dev irregularity indicates {avgBugGrowth > 30 && avgDevIrregularity > 20 ? 'elevated instability requiring attention' : 'stable performance'}. Trend: {data.length > 1 && data[data.length - 1].bugGrowth > data[0].bugGrowth ? 'increasing' : 'decreasing'}.
      </div>
    </div>
  );
};
