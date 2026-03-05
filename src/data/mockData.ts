import type { SystemData } from '../types';

export const mockSystemData: SystemData = {
  metrics: {
    failureRiskScore: 32,
    lastUpdated: new Date().toISOString(),
    systemHealth: 'Nominal',
  },
  signals: [
    {
      id: '1',
      timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
      message: 'No repository analyzed yet — enter a GitHub repo above to begin real analysis',
      status: 'Neutral',
      source: 'commit',
    },
    {
      id: '2',
      timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
      message: 'System ready: NLP engine and risk scoring algorithms initialized',
      status: 'Neutral',
      source: 'issue',
    },
  ],
  temporalData: [
    { timestamp: 'T-6', bugGrowth: 0, devIrregularity: 0 },
    { timestamp: 'T-5', bugGrowth: 0, devIrregularity: 0 },
    { timestamp: 'T-4', bugGrowth: 0, devIrregularity: 0 },
    { timestamp: 'T-3', bugGrowth: 0, devIrregularity: 0 },
    { timestamp: 'T-2', bugGrowth: 0, devIrregularity: 0 },
    { timestamp: 'T-1', bugGrowth: 0, devIrregularity: 0 },
    { timestamp: 'Now', bugGrowth: 0, devIrregularity: 0 },
  ],
  aiInsights: {
    title: 'Awaiting Repository Analysis',
    description:
      'Enter a public GitHub repository (e.g. TejasKeerthi/ART-VAULT) above and click Analyze. The system will fetch real commits, issues, and pull requests, then run NLP sentiment analysis, intent classification, and risk scoring to produce accurate reliability metrics.',
    factors: [
      'Analyze any public GitHub repository in real time',
      'NLP-powered commit message sentiment & intent analysis',
      'Automated bug detection from commit patterns',
      'Risk scoring based on issue volume, contributor activity, and code churn',
    ],
    recommendation:
      'Start by analyzing your repository to get real signals. The dashboard will populate with live data from GitHub including commit history, open issues, and pull request analysis.',
  },
};
