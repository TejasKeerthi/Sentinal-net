export interface SystemMetrics {
  failureRiskScore: number;
  lastUpdated: string;
  systemHealth: 'Critical' | 'Warning' | 'Nominal';
}

export interface SignalItem {
  id: string;
  timestamp: string;
  message: string;
  status: 'Neutral' | 'Urgent' | 'Negative';
  source: 'commit' | 'issue' | 'alert';
}

export interface TemporalDataPoint {
  timestamp: string;
  bugGrowth: number;
  devIrregularity: number;
}

export interface AIInsight {
  title: string;
  description: string;
  factors: string[];
  recommendation: string;
}

export interface SystemData {
  metrics: SystemMetrics;
  signals: SignalItem[];
  temporalData: TemporalDataPoint[];
  aiInsights: AIInsight;
}
