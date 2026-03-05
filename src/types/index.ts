export interface SystemMetrics {
  failureRiskScore: number;
  lastUpdated: string;
  systemHealth: 'Critical' | 'Warning' | 'Nominal';
  metadata?: {
    commits_30d: number;
    contributors_30d: number;
    open_issues: number;
  };
}

export interface NLPMetadata {
  intent: string;
  sentiment: string;
  risk_level: string;
  keywords: string[];
  has_urgency: boolean;
  is_bug: boolean;
}

export interface SignalItem {
  id: string;
  timestamp: string;
  message: string;
  status: 'Neutral' | 'Urgent' | 'Negative';
  source: 'commit' | 'issue' | 'alert';
  nlp?: NLPMetadata;
}

export interface TemporalDataPoint {
  timestamp: string;
  bugGrowth: number;
  devIrregularity: number;
}

export interface ConflictFile {
  file: string;
  conflict_count?: number;
  lines_in_conflict?: number;
  is_binary?: boolean;
}

export interface ConflictingPR {
  pr_number: number;
  title: string;
  files_count: number;
  additions: number;
  deletions: number;
  conflict_count: number;
  conflicted_files: string[];
  updated_at: string;
  resolution_difficulty: 'easy' | 'moderate' | 'difficult' | 'complex';
  nlp_complexity?: string;
}

export interface ConflictMetrics {
  avg_conflicts_per_pr: number;
  max_conflicts_in_single_pr: number;
  merge_conflict_rate: number;
  files_most_conflicted: ConflictFile[];
}

export interface MergeConflictData {
  total_prs_checked: number;
  prs_with_conflicts: number;
  conflict_severity: 'none' | 'low' | 'medium' | 'high' | 'critical';
  conflict_risk_score: number;
  conflicts_by_file_type: Record<string, number>;
  conflicting_prs: ConflictingPR[];
  resolution_difficulty: 'easy' | 'moderate' | 'difficult' | 'complex';
  metrics: ConflictMetrics;
}

export interface ConflictInsights {
  total_prs_checked: number;
  prs_with_conflicts: number;
  conflict_severity: 'none' | 'low' | 'medium' | 'high' | 'critical';
  resolution_difficulty: 'easy' | 'moderate' | 'difficult' | 'complex';
  conflict_rate: number;
}

export interface NLPInsights {
  bug_signals: number;
  urgent_signals: number;
  high_risk_signals: number;
  positive_sentiment: number;
  negative_sentiment: number;
  top_keywords: string[];
}

export interface AIInsight {
  title: string;
  description: string;
  factors: string[];
  recommendation: string;
  nlp_insights?: NLPInsights;
  conflict_insights?: ConflictInsights | null;
}

export interface SystemData {
  metrics: SystemMetrics;
  signals: SignalItem[];
  temporalData: TemporalDataPoint[];
  aiInsights: AIInsight;
  mergeConflicts?: MergeConflictData;
}

export interface RepoInfo {
  name: string;
  description: string;
  url: string;
  stars: number;
  forks: number;
}
