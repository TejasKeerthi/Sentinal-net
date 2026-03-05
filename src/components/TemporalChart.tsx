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
    <div 
      className="bg-gradient-to-br from-cyber-card to-darker-charcoal rounded-xl border border-cyber-gray-light p-6 cyber-border-glow hover-lift"
      style={{
        animation: 'slideInRight 0.7s ease-out'
      }}
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <TrendingUp size={28} className="text-electric-blue neon-text" />
            Temporal Trends & Analysis
          </h2>
          <p className="text-gray-400 text-xs mt-1">24-hour trend visualization with ML-powered insights</p>
        </div>
      </div>

      <div className="w-full h-96 chart-animate">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart 
            data={data} 
            margin={{ top: 10, right: 30, left: 10, bottom: 10 }}
          >
            <defs>
              {/* Gradient for Bug Growth */}
              <linearGradient id="bugGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ff6b35" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#ff6b35" stopOpacity={0.1} />
              </linearGradient>
              {/* Gradient for Dev Irregularity */}
              <linearGradient id="devGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#00d4ff" stopOpacity={0.1} />
              </linearGradient>
              {/* Glow filter */}
              <filter id="glow">
                <feGaussianBlur stdDeviation="2" result="coloredBlur" />
                <feMerge>
                  <feMergeNode in="coloredBlur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>
            
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#16213e"
              vertical={false}
              horizontalPoints={[0, 50, 100]}
            />
            
            <XAxis
              dataKey="timestamp"
              stroke="#666"
              style={{ fontSize: '12px' }}
              tick={{ fill: '#888' }}
              axisLine={{ stroke: '#16213e' }}
            />
            
            <YAxis 
              stroke="#666" 
              style={{ fontSize: '12px' }} 
              tick={{ fill: '#888' }}
              axisLine={{ stroke: '#16213e' }}
            />
            
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f0f1e',
                border: '2px solid #00d4ff',
                borderRadius: '8px',
                boxShadow: '0 0 20px rgba(0, 212, 255, 0.3)',
                transition: 'all 0.3s ease'
              }}
              labelStyle={{ color: '#00d4ff', fontWeight: 'bold' }}
              formatter={(value: any) => [
                value,
                typeof value === 'number' ? `${value}%` : value
              ]}
              cursor={{ stroke: '#00d4ff', opacity: 0.5 }}
              separator=" : "
            />
            
            <Legend
              wrapperStyle={{ 
                fontSize: '12px', 
                color: '#999',
                paddingTop: '20px',
                transition: 'all 0.3s'
              }}
              formatter={(value: any) => {
                if (value === 'bugGrowth') return '🔴 Bug Growth Rate';
                if (value === 'devIrregularity') return '🔵 Dev Irregularity';
                return value;
              }}
              verticalAlign="bottom"
              height={36}
            />
            
            {/* Bug Growth Line */}
            <Line
              type="monotone"
              dataKey="bugGrowth"
              stroke="#ff6b35"
              fill="url(#bugGradient)"
              name="bugGrowth"
              strokeWidth={3}
              dot={{ fill: '#ff6b35', r: 5, filter: 'url(#glow)' }}
              activeDot={{ r: 8, fill: '#ff8555', filter: 'url(#glow)' }}
              isAnimationActive={true}
              animationDuration={800}
            />
            
            {/* Dev Irregularity Line */}
            <Line
              type="monotone"
              dataKey="devIrregularity"
              stroke="#00d4ff"
              fill="url(#devGradient)"
              name="devIrregularity"
              strokeWidth={3}
              dot={{ fill: '#00d4ff', r: 5, filter: 'url(#glow)' }}
              activeDot={{ r: 8, fill: '#33e0ff', filter: 'url(#glow)' }}
              isAnimationActive={true}
              animationDuration={800}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Analysis Metrics */}
      <div className="mt-6 grid grid-cols-2 gap-4">
        <div className="p-4 bg-orange-900 bg-opacity-20 border border-orange-700 border-opacity-50 rounded-lg transition-all duration-300 hover:bg-opacity-30">
          <div className="text-warning-orange text-xs font-semibold mb-1">Bug Growth Average</div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-warning-orange">{avgBugGrowth}</span>
            <span className="text-xs text-gray-500">% avg</span>
          </div>
        </div>
        
        <div className="p-4 bg-electric-blue bg-opacity-20 border border-electric-blue border-opacity-50 rounded-lg transition-all duration-300 hover:bg-opacity-30">
          <div className="text-electric-blue text-xs font-semibold mb-1">Dev Irregularity Average</div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-electric-blue">{avgDevIrregularity}</span>
            <span className="text-xs text-gray-500">% avg</span>
          </div>
        </div>
      </div>

      {/* Insight Box */}
      <div 
        className="mt-6 p-4 bg-cyber-gray-light border border-cyan-700 border-opacity-30 rounded-lg transition-all duration-300 hover:border-opacity-60"
        style={{
          animation: 'slideInLeft 0.7s ease-out 0.2s backwards'
        }}
      >
        <p className="text-gray-300 text-sm leading-relaxed">
          <span className="text-electric-blue font-semibold">📊 Temporal Analysis:</span> {avgBugGrowth > 30 ? 'High' : 'Moderate'} bug growth combined with {avgDevIrregularity > 20 ? 'significant' : 'moderate'} development irregularity indicates {avgBugGrowth > 30 && avgDevIrregularity > 20 ? 'elevated system instability requiring immediate attention' : 'stable system performance with monitoring'}. Trend shows {data.length > 1 && data[data.length - 1].bugGrowth > data[0].bugGrowth ? '↗️ increasing' : '↘️ decreasing'} pattern.
        </p>
      </div>
    </div>
  );
};
