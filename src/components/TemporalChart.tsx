import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { TemporalDataPoint } from '../types';

interface TemporalChartProps {
  data: TemporalDataPoint[];
}

export const TemporalChart = ({ data }: TemporalChartProps) => {
  return (
    <div className="bg-gradient-to-br from-cyber-card to-darker-charcoal rounded-xl border border-cyber-gray-light p-6">
      <h2 className="text-2xl font-bold text-white mb-6">Temporal Trends</h2>

      <div className="w-full h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="bugGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ff6b35" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#ff6b35" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="devGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#2a2a3e"
              vertical={false}
              horizontalPoints={[0, 50, 100]}
            />
            <XAxis
              dataKey="timestamp"
              stroke="#666"
              style={{ fontSize: '12px' }}
              tick={{ fill: '#888' }}
            />
            <YAxis stroke="#666" style={{ fontSize: '12px' }} tick={{ fill: '#888' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f0f1e',
                border: '1px solid #00d4ff',
                borderRadius: '8px',
              }}
              labelStyle={{ color: '#00d4ff' }}
              formatter={(value) => [value, '']}
              cursor={{ stroke: '#00d4ff', opacity: 0.3 }}
            />
            <Legend
              wrapperStyle={{ fontSize: '12px', color: '#999' }}
              formatter={(value: any) => {
                if (value === 'bugGrowth') return 'Bug Growth Rate';
                if (value === 'devIrregularity') return 'Dev Irregularity';
                return value;
              }}
            />
            <Line
              type="monotone"
              dataKey="bugGrowth"
              stroke="#ff6b35"
              fill="url(#bugGradient)"
              name="Bug Growth"
              strokeWidth={2}
              dot={{ fill: '#ff6b35', r: 4 }}
              activeDot={{ r: 6, fill: '#ff8555' }}
              isAnimationActive={true}
            />
            <Line
              type="monotone"
              dataKey="devIrregularity"
              stroke="#00d4ff"
              fill="url(#devGradient)"
              name="Dev Irregularity"
              strokeWidth={2}
              dot={{ fill: '#00d4ff', r: 4 }}
              activeDot={{ r: 6, fill: '#33e0ff' }}
              isAnimationActive={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Info Box */}
      <div className="mt-6 p-4 bg-cyber-gray-light border border-cyber-gray rounded-lg">
        <p className="text-gray-400 text-sm">
          <span className="text-electric-blue font-semibold">Temporal Analysis:</span> Both metrics show upward trends
          over the 24-hour period. Bug growth has increased by 45% while development irregularity has surged by 35%,
          indicating growing system instability.
        </p>
      </div>
    </div>
  );
};
