/**
 * GitHub Repository Analyzer — Browser Edition
 * Calls the public GitHub REST API directly (no backend needed).
 * Performs NLP analysis on commits, issues, and PRs, then computes risk scores.
 *
 * Rate limits: unauthenticated = 60 req/h. Add a token for 5 000 req/h.
 */

import { analyze } from './nlpProcessor';
import type {
  SystemData,
  SignalItem,
  TemporalDataPoint,
  AIInsight,
} from '../types';

// ── GitHub REST helpers ──────────────────────────────────────────────────────

const GH_API = 'https://api.github.com';

interface GHCommit {
  sha: string;
  commit: {
    message: string;
    author: { date: string };
  };
  author?: { login: string } | null;
}

interface GHIssue {
  number: number;
  title: string;
  body: string | null;
  updated_at: string;
  labels: { name: string }[];
  pull_request?: unknown;
}

interface GHPull {
  number: number;
  title: string;
  body: string | null;
  updated_at: string;
  mergeable?: boolean | null;
  changed_files: number;
  additions: number;
  deletions: number;
}

interface GHRepo {
  full_name: string;
  description: string | null;
  html_url: string;
  stargazers_count: number;
  forks_count: number;
  open_issues_count: number;
}

async function ghFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${GH_API}${path}`, {
    headers: { Accept: 'application/vnd.github.v3+json' },
  });
  if (!res.ok) {
    if (res.status === 403) throw new Error('GitHub API rate limit reached. Try again in a few minutes.');
    if (res.status === 404) throw new Error('Repository not found. Check the owner/repo format.');
    throw new Error(`GitHub API error: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// ── Public entry point ──────────────────────────────────────────────────────

export async function analyzeRepository(repoPath: string): Promise<SystemData> {
  // Normalize owner/repo
  const cleaned = repoPath
    .replace(/https?:\/\/github\.com\//i, '')
    .replace(/\.git$/, '')
    .replace(/^\/|\/$/g, '');

  // Fetch repo info + recent commits + open issues in parallel
  const [repo, commits, issues, pulls] = await Promise.all([
    ghFetch<GHRepo>(`/repos/${cleaned}`),
    ghFetch<GHCommit[]>(`/repos/${cleaned}/commits?per_page=15`),
    ghFetch<GHIssue[]>(`/repos/${cleaned}/issues?state=open&sort=updated&per_page=8`),
    ghFetch<GHPull[]>(`/repos/${cleaned}/pulls?state=open&per_page=5`),
  ]);

  // Count 30-day commits (GitHub returns most-recent first; filter by date)
  const thirtyDaysAgo = new Date(Date.now() - 30 * 86400000).toISOString();
  const commits30d = commits.filter(c => c.commit.author.date >= thirtyDaysAgo);
  const contributors30d = new Set(
    commits30d.map(c => c.author?.login).filter(Boolean),
  ).size;

  // Separate real issues from PRs (GitHub issues endpoint includes PRs)
  const realIssues = issues.filter(i => !i.pull_request);
  const openIssueCount = repo.open_issues_count;

  // ── NLP analysis on signals ───────────────────────────────────────────────
  const signals: SignalItem[] = [];

  // Commits
  for (const c of commits.slice(0, 5)) {
    const msg = c.commit.message.split('\n')[0].slice(0, 120);
    const nlp = analyze(msg);
    const status: SignalItem['status'] =
      nlp.isBugRelated ? 'Urgent' : nlp.sentimentScore < -0.3 ? 'Negative' : 'Neutral';

    signals.push({
      id: c.sha.slice(0, 8),
      timestamp: c.commit.author.date,
      message: msg,
      status,
      source: 'commit',
      nlp: {
        intent: nlp.intentCategory,
        sentiment: nlp.sentimentLabel,
        risk_level: nlp.riskLevel,
        keywords: nlp.keywords.slice(0, 3),
        has_urgency: nlp.hasUrgency,
        is_bug: nlp.isBugRelated,
      },
    });
  }

  // Issues
  for (const iss of realIssues.slice(0, 3)) {
    const text = `${iss.title} ${iss.body || ''}`;
    const nlp = analyze(text);
    const status: SignalItem['status'] =
      nlp.isBugRelated || iss.title.toLowerCase().includes('bug')
        ? 'Urgent'
        : nlp.riskLevel === 'high' || nlp.riskLevel === 'critical'
          ? 'Urgent'
          : nlp.sentimentScore < -0.2
            ? 'Negative'
            : 'Neutral';

    signals.push({
      id: `issue-${iss.number}`,
      timestamp: iss.updated_at,
      message: iss.title.slice(0, 80),
      status,
      source: 'issue',
      nlp: {
        intent: nlp.intentCategory,
        sentiment: nlp.sentimentLabel,
        risk_level: nlp.riskLevel,
        keywords: nlp.keywords.slice(0, 3),
        has_urgency: nlp.hasUrgency,
        is_bug: nlp.isBugRelated,
      },
    });
  }

  // Pull requests
  for (const pr of pulls.slice(0, 2)) {
    const text = `${pr.title} ${pr.body || ''}`;
    const nlp = analyze(text);
    const status: SignalItem['status'] =
      nlp.hasUrgency || nlp.riskLevel === 'high' || nlp.riskLevel === 'critical'
        ? 'Urgent'
        : nlp.sentimentScore < -0.2
          ? 'Negative'
          : 'Neutral';

    signals.push({
      id: `pr-${pr.number}`,
      timestamp: pr.updated_at,
      message: `PR: ${pr.title.slice(0, 60)}`,
      status,
      source: 'alert',
      nlp: {
        intent: nlp.intentCategory,
        sentiment: nlp.sentimentLabel,
        risk_level: nlp.riskLevel,
        keywords: nlp.keywords.slice(0, 3),
        has_urgency: nlp.hasUrgency,
        is_bug: nlp.isBugRelated,
      },
    });
  }

  // ── Risk score calculation (NLP-enhanced, matches Python algo) ────────────
  let riskScore = 30; // neutral base

  // NLP risk signals from sampled commits
  const nlpResults = commits.slice(0, 15).map(c =>
    analyze(c.commit.message.split('\n')[0]),
  );
  const bugCount = nlpResults.filter(a => a.isBugRelated).length;
  const urgentCount = nlpResults.filter(a => a.hasUrgency).length;
  const highRiskCount = nlpResults.filter(a => a.riskLevel === 'high' || a.riskLevel === 'critical').length;
  const positiveCount = nlpResults.filter(a => a.sentimentLabel === 'positive').length;

  if (nlpResults.length > 0) {
    const bugRatio = bugCount / nlpResults.length;
    riskScore += Math.round(bugRatio * 20);
    riskScore += urgentCount * 4;
    riskScore += highRiskCount * 5;
    riskScore -= Math.round(positiveCount * 1.5);
  }

  // Issue-to-commit ratio risk
  const commitsCount = commits30d.length;
  if (commitsCount > 0) {
    const issueRatio = openIssueCount / Math.max(commitsCount, 1);
    if (issueRatio > 2.0) riskScore += 15;
    else if (issueRatio > 1.0) riskScore += 8;
    else if (issueRatio > 0.5) riskScore += 3;
  }

  // Open issue volume
  if (openIssueCount > 100) riskScore += 12;
  else if (openIssueCount > 50) riskScore += 8;
  else if (openIssueCount > 20) riskScore += 4;

  // Activity risk
  if (commitsCount === 0) riskScore += 20;
  else if (commitsCount < 3) riskScore += 10;

  // Contributor coordination risk
  if (contributors30d > 30) riskScore += 8;
  else if (contributors30d > 15) riskScore += 4;

  // Healthy active project bonus
  if (commitsCount > 20 && openIssueCount < 10 && contributors30d >= 2) {
    riskScore -= 10;
  }

  riskScore = Math.max(0, Math.min(100, Math.round(riskScore)));

  const systemHealth: 'Critical' | 'Warning' | 'Nominal' =
    riskScore > 85 ? 'Critical' : riskScore > 70 ? 'Warning' : 'Nominal';

  // ── Temporal trends (last 7 days from commit timestamps) ──────────────────
  const temporalData: TemporalDataPoint[] = [];
  for (let day = 6; day >= 0; day--) {
    const dayStart = new Date(Date.now() - day * 86400000);
    dayStart.setHours(0, 0, 0, 0);
    const dayEnd = new Date(dayStart.getTime() + 86400000);

    const dayCommits = commits.filter(c => {
      const d = new Date(c.commit.author.date);
      return d >= dayStart && d < dayEnd;
    });

    temporalData.push({
      timestamp: day === 0 ? 'Today' : `${day}d ago`,
      bugGrowth: Math.max(10, dayCommits.length * 2),
      devIrregularity: dayCommits.length > 0 ? Math.min(50, Math.floor(dayCommits.length / 2)) : 10,
    });
  }

  // ── AI insights generation ────────────────────────────────────────────────
  const bugSignals = signals.filter(s => s.nlp?.is_bug);
  const urgentSignals = signals.filter(s => s.status === 'Urgent');
  const highRiskSignals = signals.filter(s => s.nlp?.risk_level === 'high' || s.nlp?.risk_level === 'critical');
  const sentimentPos = signals.filter(s => s.nlp?.sentiment === 'positive').length;
  const sentimentNeg = signals.filter(s => s.nlp?.sentiment === 'negative').length;

  let insightTitle: string;
  if (highRiskSignals.length > 0) insightTitle = 'Critical Issues Detected in Repository';
  else if (bugSignals.length >= 2) insightTitle = 'Multiple Bug Fixes Identified';
  else if (riskScore > 70) insightTitle = 'Elevated Software Reliability Risk';
  else if (commitsCount === 0) insightTitle = 'Inactive Repository Detected';
  else if (openIssueCount > 20) insightTitle = 'High Open Issue Count';
  else insightTitle = 'Repository Activity Analysis';

  const factors: string[] = [];
  if (bugSignals.length > 0) factors.push(`Bug fixes detected in ${bugSignals.length} recent signals`);
  if (urgentSignals.length > 0) factors.push(`Urgent items identified: ${urgentSignals.length} signals require attention`);
  if (highRiskSignals.length > 0) factors.push(`High-risk signals: ${highRiskSignals.length} items flagged for review`);
  if (commitsCount > 0) factors.push(`Recent activity: ${commitsCount} commits by ${contributors30d} contributors in 30 days`);
  else factors.push('No commits in the last 30 days — repository appears inactive');
  if (openIssueCount > 0) factors.push(`Open issues: ${openIssueCount}`);
  if (factors.length === 0) factors.push('Repository analyzed successfully');

  let description = `NLP Analysis of ${repo.full_name}: `;
  if (sentimentNeg > sentimentPos) description += 'Development signals show predominantly negative sentiment. ';
  else if (sentimentPos > sentimentNeg) description += 'Development signals show positive progress momentum. ';
  else description += 'Development signals are balanced. ';
  description += factors.slice(0, 3).join('. ');

  let recommendation = 'Recommendations: ';
  if (bugSignals.length > 2) recommendation += 'Prioritize bug fixes and quality assurance testing. ';
  if (riskScore > 70) recommendation += 'Conduct thorough code review and increase test coverage. ';
  if (openIssueCount > 20) recommendation += 'Create issue triage process and assign priority labels. ';
  if (sentimentNeg > sentimentPos) recommendation += 'Investigate root causes of negative development signals. ';
  if (recommendation === 'Recommendations: ') recommendation += 'Continue current development practices. Review recent commits regularly.';

  const aiInsights: AIInsight = {
    title: insightTitle,
    description,
    factors,
    recommendation,
    nlp_insights: {
      bug_signals: bugSignals.length,
      urgent_signals: urgentSignals.length,
      high_risk_signals: highRiskSignals.length,
      positive_sentiment: sentimentPos,
      negative_sentiment: sentimentNeg,
      top_keywords: [...new Set(signals.flatMap(s => s.nlp?.keywords ?? []))].slice(0, 5),
    },
  };

  return {
    metrics: {
      failureRiskScore: riskScore,
      lastUpdated: new Date().toISOString(),
      systemHealth,
      metadata: {
        commits_30d: commitsCount,
        contributors_30d: contributors30d,
        open_issues: openIssueCount,
      },
    },
    signals: signals.slice(0, 6),
    temporalData,
    aiInsights,
  };
}
