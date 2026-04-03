import type { SystemData } from '../types';

const API_BASE_URL = (
  ((import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim() ||
    (import.meta.env.VITE_API_URL as string | undefined)?.trim() ||
    'http://localhost:8000')
).replace(/\/$/, '');

const IS_BROWSER = typeof window !== 'undefined';
const IS_LOCALHOST = IS_BROWSER
  ? ['localhost', '127.0.0.1'].includes(window.location.hostname)
  : false;
const USES_LOCAL_BACKEND = /^(https?:\/\/)?(localhost|127\.0\.0\.1)(:\d+)?$/i.test(API_BASE_URL);
const GITHUB_API_BASE = 'https://api.github.com';
const GITHUB_TOKEN = (import.meta.env.VITE_GITHUB_TOKEN as string | undefined)?.trim() || '';

interface ApiErrorPayload {
  error?: {
    code?: string;
    message?: string;
    details?: unknown;
  };
}

interface GitHubRepo {
  full_name: string;
  description: string | null;
  html_url: string;
  stargazers_count: number;
  forks_count: number;
  open_issues_count: number;
}

interface GitHubCommit {
  sha: string;
  commit: {
    message: string;
    author: {
      date: string;
      name: string;
    };
  };
  author: {
    login: string;
  } | null;
}

interface GitHubIssue {
  id: number;
  number: number;
  title: string;
  updated_at: string;
  pull_request?: unknown;
}

interface GitHubPull {
  id: number;
  number: number;
  title: string;
}

interface GitHubContributor {
  login: string;
}

interface GitHubApiError {
  message?: string;
}

function getBrowserToken(): string {
  if (typeof window === 'undefined') return '';
  try {
    const saved = window.localStorage.getItem('sentinel_github_token')?.trim() || '';
    return saved;
  } catch {
    return '';
  }
}

function githubHeaders(): Record<string, string> {
  const token = getBrowserToken() || GITHUB_TOKEN;
  const headers: Record<string, string> = {
    Accept: 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
}

function scoreRisk(params: {
  commits30d: number;
  contributors30d: number;
  openIssues: number;
  closedIssues30d: number;
  openPrs: number;
}): number {
  const { commits30d, contributors30d, openIssues, closedIssues30d, openPrs } = params;
  const issuePressure = openIssues / Math.max(commits30d, 1);
  const closureRatio = closedIssues30d / Math.max(openIssues + closedIssues30d, 1);
  const collaboration = contributors30d / Math.max(commits30d, 1);

  let risk = 35;
  risk += Math.min(30, issuePressure * 10);
  risk += Math.min(20, openPrs * 0.9);
  risk -= Math.min(18, closureRatio * 22);
  risk -= Math.min(10, collaboration * 35);

  return Math.max(5, Math.min(95, Math.round(risk)));
}

function healthFromRisk(score: number): 'Critical' | 'Warning' | 'Nominal' {
  if (score >= 80) return 'Critical';
  if (score >= 55) return 'Warning';
  return 'Nominal';
}

function statusFromText(text: string): 'Neutral' | 'Urgent' | 'Negative' {
  const normalized = text.toLowerCase();
  if (/critical|urgent|outage|incident|security|hotfix/.test(normalized)) return 'Urgent';
  if (/fail|broken|error|bug|regression|revert/.test(normalized)) return 'Negative';
  return 'Neutral';
}

async function githubGet<T>(path: string): Promise<T> {
  const response = await fetch(`${GITHUB_API_BASE}${path}`, {
    headers: githubHeaders(),
  });

  if (!response.ok) {
    let message = `GitHub request failed (${response.status})`;
    try {
      const payload = (await response.json()) as GitHubApiError;
      if (payload?.message) message = payload.message;
    } catch {
      // noop
    }

    if (response.status === 403 && /rate limit|secondary rate limit/i.test(message)) {
      throw new Error('GitHub API rate limit reached. Add your own token in localStorage key sentinel_github_token for higher limits.');
    }
    throw new Error(message);
  }

  return (await response.json()) as T;
}

async function analyzeRepositoryDirect(repo: string): Promise<SystemData> {
  const since = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString();

  const [repoInfo, commits, openIssuesRaw, closedIssuesRaw, pulls, contributors] = await Promise.all([
    githubGet<GitHubRepo>(`/repos/${repo}`),
    githubGet<GitHubCommit[]>(`/repos/${repo}/commits?since=${encodeURIComponent(since)}&per_page=60`),
    githubGet<GitHubIssue[]>(`/repos/${repo}/issues?state=open&sort=updated&per_page=30`),
    githubGet<GitHubIssue[]>(`/repos/${repo}/issues?state=closed&since=${encodeURIComponent(since)}&per_page=30`),
    githubGet<GitHubPull[]>(`/repos/${repo}/pulls?state=open&per_page=30`),
    githubGet<GitHubContributor[]>(`/repos/${repo}/contributors?per_page=30`),
  ]);

  const openIssues = openIssuesRaw.filter((i) => !i.pull_request);
  const closedIssues30d = closedIssuesRaw.filter((i) => !i.pull_request);

  const commits30d = commits.length;
  const contributors30d = contributors.length || new Set(commits.map((c) => c.author?.login || c.commit.author.name)).size;
  const openPrs = pulls.length;

  const riskScore = scoreRisk({
    commits30d,
    contributors30d,
    openIssues: openIssues.length,
    closedIssues30d: closedIssues30d.length,
    openPrs,
  });

  const commitSignals = commits.slice(0, 4).map((c) => {
    const message = c.commit.message.split('\n')[0].slice(0, 140);
    return {
      id: c.sha.slice(0, 8),
      timestamp: c.commit.author.date,
      message,
      status: statusFromText(message),
      source: 'commit' as const,
    };
  });

  const issueSignals = openIssues.slice(0, 3).map((i) => ({
    id: `issue-${i.number}`,
    timestamp: i.updated_at,
    message: i.title.slice(0, 140),
    status: statusFromText(i.title),
    source: 'issue' as const,
  }));

  const dayLabels = ['6d ago', '5d ago', '4d ago', '3d ago', '2d ago', '1d ago', 'Today'];
  const dailyCounts = new Array<number>(7).fill(0);
  for (const c of commits) {
    const daysAgo = Math.floor((Date.now() - new Date(c.commit.author.date).getTime()) / (24 * 60 * 60 * 1000));
    if (daysAgo >= 0 && daysAgo < 7) {
      dailyCounts[6 - daysAgo] += 1;
    }
  }

  const temporalData = dayLabels.map((label, idx) => {
    const count = dailyCounts[idx];
    return {
      timestamp: label,
      bugGrowth: Math.min(100, count * 8 + (riskScore > 60 ? 15 : 5)),
      devIrregularity: Math.min(100, Math.abs(count - (commits30d / 7)) * 8 + 10),
    };
  });

  const confidence = 0.79;
  const nlpScore = Math.min(100, Math.round((issueSignals.filter((s) => s.status !== 'Neutral').length / Math.max(issueSignals.length, 1)) * 100));

  return {
    metrics: {
      failureRiskScore: riskScore,
      lastUpdated: new Date().toISOString(),
      systemHealth: healthFromRisk(riskScore),
      metadata: {
        commits_30d: commits30d,
        contributors_30d: contributors30d,
        open_issues: openIssues.length,
        closed_issues_30d: closedIssues30d.length,
        open_prs: openPrs,
        model_name: 'GitHubLiveHeuristic',
        model_version: '1.0.0',
        ml_prediction: riskScore,
        nlp_signal_score: nlpScore,
        blended_score: riskScore,
        confidence,
        uncertainty: 1 - confidence,
        contributing_factors: {
          issue_pressure: Math.min(1, openIssues.length / Math.max(commits30d, 1)),
          open_pr_load: Math.min(1, openPrs / 30),
          closure_velocity: Math.min(1, closedIssues30d.length / Math.max(openIssues.length + closedIssues30d.length, 1)),
        },
      },
    },
    signals: [...commitSignals, ...issueSignals],
    temporalData,
    aiInsights: {
      title: `${repoInfo.full_name} live reliability snapshot`,
      description: `Real-time GitHub analysis based on commits, issues, and pull requests from the last 30 days.`,
      factors: [
        `Open issues: ${openIssues.length}`,
        `Open pull requests: ${openPrs}`,
        `Commits in 30d: ${commits30d}`,
        `Contributors in 30d: ${contributors30d}`,
      ],
      recommendation: 'Prioritize high-risk issue triage and reduce open PR backlog to improve reliability posture.',
      nlp_insights: {
        bug_signals: issueSignals.filter((s) => /bug|fix|error|fail/i.test(s.message)).length,
        urgent_signals: issueSignals.filter((s) => s.status === 'Urgent').length,
        high_risk_signals: issueSignals.filter((s) => s.status !== 'Neutral').length,
        positive_sentiment: 0,
        negative_sentiment: issueSignals.filter((s) => s.status === 'Negative').length,
        top_keywords: ['github', 'issues', 'prs', 'commits', 'reliability'],
      },
    },
    repoInfo: {
      name: repoInfo.full_name,
      description: repoInfo.description || 'No description available',
      url: repoInfo.html_url,
      stars: repoInfo.stargazers_count,
      forks: repoInfo.forks_count,
    },
    riskBreakdown: {
      risk_score: riskScore,
      confidence,
      uncertainty: 1 - confidence,
      ml_risk_score: riskScore,
      nlp_signal_score: nlpScore,
      blended_risk_score: riskScore,
      reasoning_factors: {
        issue_pressure: Math.min(1, openIssues.length / Math.max(commits30d, 1)),
        open_pr_load: Math.min(1, openPrs / 30),
        closure_velocity: Math.min(1, closedIssues30d.length / Math.max(openIssues.length + closedIssues30d.length, 1)),
      },
    },
  };
}

async function readError(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as ApiErrorPayload;
    if (payload?.error?.message) {
      return payload.error.message;
    }
  } catch {
    // Ignore parse errors and fallback to status text.
  }

  if (response.status === 404) {
    return 'Repository not found. Check owner/repo format.';
  }
  if (response.status === 422) {
    return 'Invalid request payload. Please check input fields.';
  }
  if (response.status >= 500) {
    return 'Backend error while analyzing repository.';
  }
  return `Request failed (${response.status})`;
}

export async function analyzeRepository(repoPath: string): Promise<SystemData> {
  const repo = repoPath
    .replace(/https?:\/\/github\.com\//i, '')
    .replace(/\.git$/i, '')
    .replace(/^\/|\/$/g, '');

  if (!repo || !repo.includes('/')) {
    throw new Error('Please enter a valid repository in owner/repo format.');
  }

  if (!IS_LOCALHOST && USES_LOCAL_BACKEND) {
    return analyzeRepositoryDirect(repo);
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/repository/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ repo }),
    });
  } catch {
    return analyzeRepositoryDirect(repo);
  }

  if (!response.ok) {
    const backendError = await readError(response);
    if (/rate limit|backend error|request failed|unavailable|timeout|network/i.test(backendError)) {
      return analyzeRepositoryDirect(repo);
    }
    throw new Error(backendError);
  }

  return (await response.json()) as SystemData;
}

export async function getSystemData(): Promise<SystemData> {
  const response = await fetch(`${API_BASE_URL}/api/system-data`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(await readError(response));
  }

  return (await response.json()) as SystemData;
}
