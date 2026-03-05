/**
 * NLP Processor for Sentinel-Net (Browser Edition)
 * Ports the Python NLP logic to TypeScript.
 * Performs sentiment analysis, intent classification, risk scoring, and keyword extraction
 * entirely in the browser — no backend needed.
 */

// ── Types ──────────────────────────────────────────────────────────────────────

export interface NLPAnalysis {
  text: string;
  sentimentScore: number;   // -1 to 1
  sentimentLabel: 'negative' | 'neutral' | 'positive';
  intentCategory: string;   // bug_fix, feature, refactor, docs, chore, test, security, unknown
  intentConfidence: number; // 0 to 1
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  riskScore: number;        // 0 to 1
  keywords: string[];
  hasUrgency: boolean;
  isBugRelated: boolean;
  factors: string[];
}

// ── Keyword dictionaries ────────────────────────────────────────────────────────

const INTENT_KEYWORDS: Record<string, RegExp[]> = {
  bug_fix: [/fix/i, /bug/i, /issue/i, /broken/i, /crash/i, /error/i, /patch/i, /resolve/i, /correction/i, /regression/i, /hotfix/i],
  feature: [/add/i, /new/i, /feature/i, /implement/i, /support/i, /enable/i, /introduce/i, /launch/i, /beta/i],
  refactor: [/refactor/i, /cleanup/i, /clean up/i, /simplify/i, /improve/i, /optimize/i, /enhance/i, /restructure/i, /reorganize/i],
  docs: [/doc/i, /documentation/i, /readme/i, /comment/i, /update docs/i],
  test: [/test/i, /testing/i, /coverage/i, /assert/i, /unittest/i, /pytest/i, /tdd/i],
  security: [/security/i, /vulnerab/i, /cve/i, /xss/i, /sql/i, /csrf/i, /exploit/i, /breach/i, /auth/i, /encrypt/i],
  chore: [/chore/i, /bump/i, /update/i, /upgrade/i, /version/i, /dependency/i, /merge/i, /sync/i],
};

const HIGH_RISK_PATTERNS = [
  /critical/i, /severe/i, /emergency/i, /urgent/i, /asap/i,
  /crash/i, /data loss/i, /memory leak/i, /infinite loop/i,
  /security/i, /vulnerab/i, /exploit/i, /breach/i,
];

const URGENCY_PATTERNS = [
  /urgent/i, /asap/i, /emergency/i, /critical/i, /immediately/i,
  /\bnow\b/i, /hotfix/i, /\bdown\b/i, /outage/i,
];

const BUG_KEYWORDS = [
  /bug/i, /fix/i, /crash/i, /error/i, /broken/i, /issue/i,
  /regression/i, /fail/i, /exception/i, /undefined/i, /\bnull\b/i,
];

const STOP_WORDS = new Set([
  'a', 'an', 'and', 'the', 'is', 'to', 'in', 'for', 'of', 'with',
  'from', 'by', 'on', 'at', 'this', 'that', 'was', 'were', 'are',
  'been', 'being', 'have', 'has', 'had', 'will', 'would', 'could',
  'should', 'shall', 'may', 'might', 'must', 'need', 'also', 'just',
  'about', 'into', 'some', 'than', 'then', 'when', 'where', 'which',
  'while', 'after', 'before', 'more', 'most', 'only', 'very',
]);

// ── Lightweight VADER-style sentiment scoring ────────────────────────────────
// We use a curated word list rather than shipping a 7,000-word lexicon.

const POS_WORDS = new Set([
  'good', 'great', 'awesome', 'excellent', 'nice', 'clean', 'improve',
  'improved', 'better', 'best', 'success', 'resolved', 'complete',
  'completed', 'perfect', 'happy', 'stable', 'solid', 'robust',
  'efficient', 'fast', 'working', 'reliable', 'safe', 'secure',
  'enhance', 'enhanced', 'optimized', 'fixed', 'ready', 'done',
]);

const NEG_WORDS = new Set([
  'bad', 'broken', 'bug', 'crash', 'error', 'fail', 'failed', 'failure',
  'wrong', 'issue', 'problem', 'critical', 'severe', 'urgent', 'hack',
  'vulnerability', 'exploit', 'leak', 'slow', 'unstable', 'deprecated',
  'regression', 'conflict', 'blocking', 'blocked', 'outage', 'exception',
  'undefined', 'null', 'corrupt', 'corrupted', 'loss', 'missing',
]);

function sentimentScore(text: string): number {
  const words = text.toLowerCase().split(/\W+/).filter(Boolean);
  if (words.length === 0) return 0;
  let score = 0;
  for (const w of words) {
    if (POS_WORDS.has(w)) score += 1;
    if (NEG_WORDS.has(w)) score -= 1;
  }
  // Normalize roughly to -1..1
  return Math.max(-1, Math.min(1, score / Math.max(words.length * 0.3, 1)));
}

// ── Public API ──────────────────────────────────────────────────────────────────

export function analyze(text: string): NLPAnalysis {
  const lower = text.toLowerCase().trim();

  // Sentiment
  const sScore = sentimentScore(lower);
  const sLabel: NLPAnalysis['sentimentLabel'] =
    sScore < -0.1 ? 'negative' : sScore > 0.1 ? 'positive' : 'neutral';

  // Intent classification
  let bestCategory = 'unknown';
  let maxMatches = 0;
  for (const [category, patterns] of Object.entries(INTENT_KEYWORDS)) {
    const matches = patterns.reduce((n, rx) => n + (rx.test(lower) ? 1 : 0), 0);
    if (matches > maxMatches) {
      maxMatches = matches;
      bestCategory = category;
    }
  }
  const intentConfidence = maxMatches > 0 ? Math.min(maxMatches / 5, 1) : 0;

  // Risk scoring
  let rScore = 0.3;
  const highRiskHits = HIGH_RISK_PATTERNS.reduce((n, rx) => n + (rx.test(lower) ? 1 : 0), 0);
  if (highRiskHits > 0) rScore += Math.min(highRiskHits * 0.2, 0.4);
  if (sScore < -0.5) rScore += 0.15;
  else if (sScore < -0.2) rScore += 0.05;
  rScore = Math.min(rScore, 1);

  const riskLevel: NLPAnalysis['riskLevel'] =
    rScore > 0.7 ? 'critical' : rScore > 0.5 ? 'high' : rScore > 0.35 ? 'medium' : 'low';

  // Keyword extraction
  const words = lower.match(/\b[a-z]{4,}\b/g) || [];
  const keywords = [...new Set(words.filter(w => !STOP_WORDS.has(w)))].slice(0, 5);

  // Urgency & bug detection
  const hasUrgency = URGENCY_PATTERNS.some(rx => rx.test(lower));
  const isBugRelated = BUG_KEYWORDS.some(rx => rx.test(lower));

  // Factors
  const factors: string[] = [];
  if (sScore < -0.5) factors.push('Negative sentiment detected');
  else if (sScore > 0.3) factors.push('Positive sentiment in message');
  factors.push(`Classification: ${bestCategory.replace('_', ' ')}`);
  factors.push(`Risk level: ${riskLevel}`);
  if (hasUrgency) factors.push('Urgent language detected');

  return {
    text,
    sentimentScore: sScore,
    sentimentLabel: sLabel,
    intentCategory: bestCategory,
    intentConfidence,
    riskLevel,
    riskScore: rScore,
    keywords,
    hasUrgency,
    isBugRelated,
    factors,
  };
}
