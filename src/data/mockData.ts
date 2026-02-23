import type { SystemData } from '../types';

export const mockSystemData: SystemData = {
  metrics: {
    failureRiskScore: 72,
    lastUpdated: new Date().toISOString(),
    systemHealth: 'Warning',
  },
  signals: [
    {
      id: '1',
      timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
      message: 'Critical bug detected in authentication module - fix regression in login flow',
      status: 'Urgent',
      source: 'commit',
    },
    {
      id: '2',
      timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
      message: 'Refactored database connection pooling - improved response times',
      status: 'Neutral',
      source: 'issue',
    },
    {
      id: '3',
      timestamp: new Date(Date.now() - 25 * 60000).toISOString(),
      message: 'Memory leak detected in WebSocket handler - investigating root cause',
      status: 'Negative',
      source: 'alert',
    },
    {
      id: '4',
      timestamp: new Date(Date.now() - 35 * 60000).toISOString(),
      message: 'Deployed security patch for dependency vulnerability - CVE-2026-0123',
      status: 'Neutral',
      source: 'commit',
    },
    {
      id: '5',
      timestamp: new Date(Date.now() - 45 * 60000).toISOString(),
      message: 'Unusual spike in error rates detected - correlation with increased traffic',
      status: 'Negative',
      source: 'alert',
    },
    {
      id: '6',
      timestamp: new Date(Date.now() - 55 * 60000).toISOString(),
      message: 'Optimized API response time from 850ms to 120ms - cache layer implementation',
      status: 'Neutral',
      source: 'commit',
    },
  ],
  temporalData: [
    { timestamp: '00:00', bugGrowth: 12, devIrregularity: 8 },
    { timestamp: '04:00', bugGrowth: 18, devIrregularity: 12 },
    { timestamp: '08:00', bugGrowth: 24, devIrregularity: 15 },
    { timestamp: '12:00', bugGrowth: 32, devIrregularity: 22 },
    { timestamp: '16:00', bugGrowth: 38, devIrregularity: 28 },
    { timestamp: '20:00', bugGrowth: 42, devIrregularity: 32 },
    { timestamp: '24:00', bugGrowth: 45, devIrregularity: 35 },
  ],
  aiInsights: {
    title: 'Elevated Risk Detected',
    description:
      'The current failure risk score of 72% indicates elevated vulnerability in production systems. Analysis reveals three primary contributing factors: increased bug growth trajectory (45 new issues detected), abnormal development irregularity patterns (unusual commit volatility), and memory management concerns in critical components.',
    factors: [
      'Bug growth rate: +48% over 24 hours',
      'Development irregularity: 35% above baseline',
      'Memory leak in WebSocket handler',
      'Unresolved authentication regression',
      'Increased error rate correlation with traffic spikes',
    ],
    recommendation:
      'Immediate action recommended: 1) Prioritize WebSocket memory leak investigation, 2) Conduct emergency review of authentication module, 3) Implement circuit breaker for traffic spike mitigation, 4) Schedule focused refactoring session to reduce development irregularity.',
  },
};
