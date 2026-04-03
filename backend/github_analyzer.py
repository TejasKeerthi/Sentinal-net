"""
GitHub repository analyzer for Sentinel-Net.
Collects repository signals, runs NLP classification, computes engineered
features, and invokes the trained ML model for risk scoring.
"""

from __future__ import annotations

import os
import importlib
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from ml_models import get_risk_predictor
from nlp_processor import get_processor

try:
    _dotenv = importlib.import_module("dotenv")
    find_dotenv = getattr(_dotenv, "find_dotenv")
    load_dotenv = getattr(_dotenv, "load_dotenv")
    DOTENV_AVAILABLE = True
except Exception:
    DOTENV_AVAILABLE = False

try:
    from github import Github, GithubException

    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False


if DOTENV_AVAILABLE:
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path=dotenv_path, override=False)


class GitHubAnalyzer:
    def __init__(self, github_token: str | None = None) -> None:
        self.token = github_token or os.getenv("GITHUB_TOKEN") or os.getenv("VITE_GITHUB_TOKEN")
        self.client = Github(self.token) if GITHUB_AVAILABLE else None
        self._cache_ttl_seconds = max(0, int(os.getenv("GITHUB_ANALYSIS_CACHE_TTL", "300")))
        self._cache: Dict[str, Tuple[datetime, Dict[str, Any]]] = {}

    def analyze_repo(self, repo_url: str) -> Dict[str, Any]:
        repo_path = self._extract_repo_path(repo_url)
        cached = self._get_cached(repo_path)
        if cached is not None:
            return cached

        if not GITHUB_AVAILABLE or self.client is None:
            return self._fallback_analysis(repo_path, "PyGithub unavailable, using synthetic repo profile")

        try:
            repo = self.client.get_repo(repo_path)
        except GithubException as exc:
            if self._is_rate_limit_error(exc):
                stale = self._get_cached(repo_path, allow_stale=True)
                if stale is not None:
                    return stale
                return self._fallback_analysis(repo_path, self._rate_limit_message(exc))
            return self._fallback_analysis(repo_path, f"GitHub API error: {exc.data if hasattr(exc, 'data') else str(exc)}")
        except Exception as exc:
            return self._fallback_analysis(repo_path, f"Repository fetch error: {str(exc)}")

        try:
            commits_30d, commits_sample = self._recent_commits(repo, limit=80)
            contributors_30d = self._count_contributors(commits_sample)
            open_issues = int(repo.open_issues_count)
            closed_issues_30d = self._count_closed_issues(repo)
            open_prs, prs_sample = self._open_prs(repo)

            signals = self._extract_signals(commits_sample, repo)
            temporal_data = self._temporal_trends(commits_sample)
            nlp_score, nlp_insights = self._nlp_signal_score(signals)

            features = self._engineer_features(
                commits_30d=commits_30d,
                contributors_30d=contributors_30d,
                open_issues=open_issues,
                closed_issues_30d=closed_issues_30d,
                open_prs=open_prs,
                signals=signals,
                prs_sample=prs_sample,
            )

            predictor = get_risk_predictor()
            prediction = predictor.predict(features, nlp_signal_score=nlp_score, blend_alpha=0.82)

            risk_score = int(round(prediction.predicted_risk_score))
            health = self._health_from_score(risk_score)
            ai_insight = self._build_ai_insight(
                repo_name=repo.full_name,
                risk_score=risk_score,
                features=features,
                nlp_insights=nlp_insights,
                prediction_factors=prediction.contributing_factors,
            )

            metadata = {
                "commits_30d": commits_30d,
                "contributors_30d": contributors_30d,
                "open_issues": open_issues,
                "closed_issues_30d": closed_issues_30d,
                "open_prs": open_prs,
                "model_name": prediction.model_name,
                "model_version": prediction.model_version,
                "ml_prediction": prediction.ml_risk_score,
                "nlp_signal_score": prediction.nlp_signal_score,
                "blended_score": prediction.blended_risk_score,
                "confidence": prediction.confidence,
                "uncertainty": prediction.uncertainty,
                "contributing_factors": prediction.contributing_factors,
            }

            result = {
                "metrics": {
                    "failureRiskScore": risk_score,
                    "lastUpdated": datetime.utcnow().isoformat() + "Z",
                    "systemHealth": health,
                    "metadata": metadata,
                },
                "signals": signals,
                "temporalData": temporal_data,
                "aiInsights": ai_insight,
                "repoInfo": {
                    "name": repo.full_name,
                    "description": repo.description,
                    "url": repo.html_url,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                },
                "riskBreakdown": {
                    "risk_score": risk_score,
                    "confidence": prediction.confidence,
                    "uncertainty": prediction.uncertainty,
                    "ml_risk_score": prediction.ml_risk_score,
                    "nlp_signal_score": prediction.nlp_signal_score,
                    "blended_risk_score": prediction.blended_risk_score,
                    "reasoning_factors": prediction.contributing_factors,
                },
            }
            self._set_cache(repo_path, result)
            return result

        except GithubException as exc:
            if self._is_rate_limit_error(exc):
                stale = self._get_cached(repo_path, allow_stale=True)
                if stale is not None:
                    return stale
                return self._fallback_analysis(repo_path, self._rate_limit_message(exc))
            return self._fallback_analysis(repo_path, f"GitHub API error during analysis: {str(exc)}")
        except Exception as exc:
            return self._fallback_analysis(repo_path, f"Analysis pipeline error: {str(exc)}")

    def _get_cached(self, repo_path: str, allow_stale: bool = False) -> Dict[str, Any] | None:
        entry = self._cache.get(repo_path)
        if entry is None:
            return None

        cached_at, payload = entry
        age_seconds = (datetime.utcnow() - cached_at).total_seconds()
        is_fresh = age_seconds <= self._cache_ttl_seconds

        if not is_fresh and not allow_stale:
            self._cache.pop(repo_path, None)
            return None

        cached_payload = deepcopy(payload)
        metadata = cached_payload.setdefault("metrics", {}).setdefault("metadata", {})
        metadata["cache_age_seconds"] = int(max(age_seconds, 0))
        metadata["cache_ttl_seconds"] = self._cache_ttl_seconds
        metadata["from_cache"] = True

        if allow_stale and not is_fresh:
            cached_payload["warning"] = "Using stale cached analysis because GitHub API rate limit was exceeded."

        return cached_payload

    def _set_cache(self, repo_path: str, payload: Dict[str, Any]) -> None:
        self._cache[repo_path] = (datetime.utcnow(), deepcopy(payload))

    def _is_rate_limit_error(self, exc: GithubException) -> bool:
        status = getattr(exc, "status", None)
        data = getattr(exc, "data", None)
        message = str(exc).lower()

        if isinstance(data, dict):
            api_message = str(data.get("message", "")).lower()
            message = f"{message} {api_message}".strip()

        if "rate limit" in message or "abuse detection" in message:
            return True

        return status in {403, 429} and ("limit" in message or "abuse" in message)

    def _rate_limit_message(self, exc: GithubException) -> str:
        base = "GitHub API rate limit exceeded."
        if not self.token:
            base += " Configure GITHUB_TOKEN (or VITE_GITHUB_TOKEN) in .env and restart the backend."

        try:
            reset_at = self.client.rate_limiting_resettime if self.client else 0
            if reset_at:
                reset_at_iso = datetime.utcfromtimestamp(reset_at).isoformat() + "Z"
                base += f" Rate limit resets around {reset_at_iso}."
        except Exception:
            pass

        return base

    def _extract_repo_path(self, repo_url: str) -> str:
        value = repo_url.strip()
        if "github.com/" in value:
            value = value.split("github.com/")[1]
        value = value.replace(".git", "").strip("/")
        parts = value.split("/")
        if len(parts) < 2:
            raise ValueError("Repository must be in owner/repo format")
        return f"{parts[0]}/{parts[1]}"

    def _recent_commits(self, repo: Any, limit: int) -> Tuple[int, List[Any]]:
        since = datetime.utcnow() - timedelta(days=30)
        commits = list(repo.get_commits(since=since)[:limit])
        return len(commits), commits

    def _count_contributors(self, commits: List[Any]) -> int:
        unique = set()
        for commit in commits:
            if commit.author and getattr(commit.author, "login", None):
                unique.add(commit.author.login)
            elif commit.commit and commit.commit.author and commit.commit.author.email:
                unique.add(commit.commit.author.email)
        return len(unique)

    def _count_closed_issues(self, repo: Any) -> int:
        since = datetime.utcnow() - timedelta(days=30)
        closed = repo.get_issues(state="closed", since=since)
        count = 0
        for idx, issue in enumerate(closed):
            if idx >= 120:
                break
            if not issue.pull_request:
                count += 1
        return count

    def _open_prs(self, repo: Any) -> Tuple[int, List[Any]]:
        prs = list(repo.get_pulls(state="open")[:80])
        return len(prs), prs

    def _extract_signals(self, commits: List[Any], repo: Any) -> List[Dict[str, Any]]:
        nlp = get_processor()
        signals: List[Dict[str, Any]] = []

        for commit in commits[:6]:
            message = commit.commit.message.split("\n")[0][:140]
            analysis = nlp.analyze(message)
            status = self._status_from_nlp(analysis.risk_level, analysis.sentiment_score, analysis.has_urgency)
            signals.append(
                {
                    "id": commit.sha[:8],
                    "timestamp": commit.commit.author.date.isoformat() + "Z",
                    "message": message,
                    "status": status,
                    "source": "commit",
                    "nlp": {
                        "intent": analysis.intent_category,
                        "sentiment": analysis.sentiment_label,
                        "risk_level": analysis.risk_level,
                        "keywords": analysis.keywords[:4],
                        "has_urgency": analysis.has_urgency,
                        "is_bug": analysis.is_bug_related,
                    },
                }
            )

        open_issues = repo.get_issues(state="open", sort="updated")
        for issue in open_issues[:4]:
            if issue.pull_request:
                continue
            text = f"{issue.title} {issue.body or ''}"[:800]
            analysis = nlp.analyze(text)
            status = self._status_from_nlp(analysis.risk_level, analysis.sentiment_score, analysis.has_urgency)
            signals.append(
                {
                    "id": f"issue-{issue.number}",
                    "timestamp": issue.updated_at.isoformat() + "Z",
                    "message": issue.title[:120],
                    "status": status,
                    "source": "issue",
                    "nlp": {
                        "intent": analysis.intent_category,
                        "sentiment": analysis.sentiment_label,
                        "risk_level": analysis.risk_level,
                        "keywords": analysis.keywords[:4],
                        "has_urgency": analysis.has_urgency,
                        "is_bug": analysis.is_bug_related,
                    },
                }
            )

        return signals

    def _status_from_nlp(self, risk_level: str, sentiment_score: float, has_urgency: bool) -> str:
        if risk_level in {"critical", "high"} or has_urgency:
            return "Urgent"
        if sentiment_score < -0.25:
            return "Negative"
        return "Neutral"

    def _temporal_trends(self, commits: List[Any]) -> List[Dict[str, Any]]:
        now = datetime.utcnow()
        buckets: List[Dict[str, Any]] = []

        for day in range(6, -1, -1):
            start = now - timedelta(days=day)
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)

            daily_commits = [c for c in commits if start <= c.commit.author.date.replace(tzinfo=None) < end]
            bug_messages = [c for c in daily_commits if "fix" in c.commit.message.lower() or "bug" in c.commit.message.lower()]
            bug_growth = max(0, min(100, len(daily_commits) * 8 + len(bug_messages) * 6))
            irregularity = max(5, min(100, len(daily_commits) * 4))

            buckets.append(
                {
                    "timestamp": "Today" if day == 0 else f"{day}d ago",
                    "bugGrowth": bug_growth,
                    "devIrregularity": irregularity,
                }
            )

        return buckets

    def _nlp_signal_score(self, signals: List[Dict[str, Any]]) -> Tuple[float, Dict[str, Any]]:
        if not signals:
            return 15.0, {
                "bug_signals": 0,
                "urgent_signals": 0,
                "high_risk_signals": 0,
                "positive_sentiment": 0,
                "negative_sentiment": 0,
                "top_keywords": [],
            }

        bug = sum(1 for s in signals if s.get("nlp", {}).get("is_bug"))
        urgent = sum(1 for s in signals if s.get("status") == "Urgent")
        high = sum(1 for s in signals if s.get("nlp", {}).get("risk_level") in {"high", "critical"})
        pos = sum(1 for s in signals if s.get("nlp", {}).get("sentiment") == "positive")
        neg = sum(1 for s in signals if s.get("nlp", {}).get("sentiment") == "negative")

        keywords: List[str] = []
        for signal in signals:
            keywords.extend(signal.get("nlp", {}).get("keywords", []))

        total = max(len(signals), 1)
        score = (
            (bug / total) * 38
            + (urgent / total) * 28
            + (high / total) * 24
            + (neg / total) * 15
            - (pos / total) * 10
        )
        score = float(max(0.0, min(100.0, 18.0 + score)))

        return score, {
            "bug_signals": bug,
            "urgent_signals": urgent,
            "high_risk_signals": high,
            "positive_sentiment": pos,
            "negative_sentiment": neg,
            "top_keywords": list(dict.fromkeys(keywords))[:6],
        }

    def _engineer_features(
        self,
        commits_30d: int,
        contributors_30d: int,
        open_issues: int,
        closed_issues_30d: int,
        open_prs: int,
        signals: List[Dict[str, Any]],
        prs_sample: List[Any],
    ) -> Dict[str, float]:
        total_signals = max(len(signals), 1)
        bug_fix_ratio = sum(1 for s in signals if s.get("nlp", {}).get("is_bug")) / total_signals
        urgent_signal_ratio = sum(1 for s in signals if s.get("status") == "Urgent") / total_signals
        negative_sentiment_ratio = sum(
            1 for s in signals if s.get("nlp", {}).get("sentiment") == "negative"
        ) / total_signals

        avg_commit_frequency = commits_30d / 30.0
        code_churn_rate = min(1.0, (open_prs * 4 + commits_30d) / max(260, commits_30d * 7))
        mean_pr_cycle_time_hours = self._avg_pr_cycle_time(prs_sample)

        # These are inferred metrics when no CI/coverage feed is connected yet.
        test_coverage = max(15.0, min(95.0, 82.0 - (open_issues / max(commits_30d + 1, 1)) * 6.5))
        ci_failures_rate = max(0.02, min(0.8, urgent_signal_ratio * 0.55 + negative_sentiment_ratio * 0.3))
        release_stability_index = max(0.0, min(1.0, 1 - (urgent_signal_ratio * 0.5 + ci_failures_rate * 0.45)))

        issue_to_commit_ratio = open_issues / max(commits_30d, 1)
        bus_factor_inverse = 1 / max(1.0, contributors_30d**0.5)
        developer_load_index = (open_issues + open_prs) / max(contributors_30d, 1)
        commit_volatility = min(1.0, abs(0.5 - avg_commit_frequency / 10.0) + code_churn_rate * 0.35)

        return {
            "commits_30d": float(commits_30d),
            "contributors_30d": float(contributors_30d),
            "open_issues": float(open_issues),
            "closed_issues_30d": float(closed_issues_30d),
            "open_prs": float(open_prs),
            "avg_commit_frequency": float(avg_commit_frequency),
            "code_churn_rate": float(code_churn_rate),
            "bug_fix_ratio": float(bug_fix_ratio),
            "urgent_signal_ratio": float(urgent_signal_ratio),
            "negative_sentiment_ratio": float(negative_sentiment_ratio),
            "test_coverage": float(test_coverage),
            "ci_failures_rate": float(ci_failures_rate),
            "mean_pr_cycle_time_hours": float(mean_pr_cycle_time_hours),
            "release_stability_index": float(release_stability_index),
            "issue_to_commit_ratio": float(issue_to_commit_ratio),
            "bus_factor_inverse": float(bus_factor_inverse),
            "developer_load_index": float(developer_load_index),
            "commit_volatility": float(commit_volatility),
        }

    def _avg_pr_cycle_time(self, prs_sample: List[Any]) -> float:
        if not prs_sample:
            return 16.0

        elapsed_hours: List[float] = []
        now = datetime.utcnow()
        for pr in prs_sample[:15]:
            created_at = pr.created_at.replace(tzinfo=None)
            updated_at = (pr.updated_at or now).replace(tzinfo=None)
            cycle = max((updated_at - created_at).total_seconds() / 3600.0, 1.0)
            elapsed_hours.append(cycle)

        if not elapsed_hours:
            return 16.0
        return sum(elapsed_hours) / len(elapsed_hours)

    def _build_ai_insight(
        self,
        repo_name: str,
        risk_score: int,
        features: Dict[str, float],
        nlp_insights: Dict[str, Any],
        prediction_factors: Dict[str, float],
    ) -> Dict[str, Any]:
        severity = "high" if risk_score >= 70 else "medium" if risk_score >= 45 else "low"
        title = f"{repo_name} reliability risk is {severity}"

        description = (
            f"Risk {risk_score}/100 is derived from a trained dual-head adaptive fusion model and NLP signal analysis. "
            f"Issue pressure ratio is {features['issue_to_commit_ratio']:.2f}, "
            f"CI failure rate estimate is {features['ci_failures_rate']:.2f}, "
            f"and urgent signal ratio is {features['urgent_signal_ratio']:.2f}."
        )

        factors = [
            f"Urgent signal ratio: {features['urgent_signal_ratio']:.2f}",
            f"Issue/commit pressure: {features['issue_to_commit_ratio']:.2f}",
            f"Estimated CI failures: {features['ci_failures_rate']:.2f}",
            f"Model dominant factor: {max(prediction_factors, key=prediction_factors.get)}",
        ]

        recommendation = (
            "Stabilize release flow by triaging open issues, reducing PR cycle time, "
            "and prioritizing tests for modules with repeated urgent/negative signals."
        )

        return {
            "title": title,
            "description": description,
            "factors": factors,
            "recommendation": recommendation,
            "nlp_insights": nlp_insights,
        }

    def _health_from_score(self, risk_score: int) -> str:
        if risk_score >= 80:
            return "Critical"
        if risk_score >= 55:
            return "Warning"
        return "Nominal"

    def _fallback_analysis(self, repo_name: str, reason: str) -> Dict[str, Any]:
        predictor = get_risk_predictor()
        features = {
            "commits_30d": 18.0,
            "contributors_30d": 4.0,
            "open_issues": 23.0,
            "closed_issues_30d": 15.0,
            "open_prs": 6.0,
            "avg_commit_frequency": 0.6,
            "code_churn_rate": 0.34,
            "bug_fix_ratio": 0.35,
            "urgent_signal_ratio": 0.28,
            "negative_sentiment_ratio": 0.22,
            "test_coverage": 71.0,
            "ci_failures_rate": 0.14,
            "mean_pr_cycle_time_hours": 21.0,
            "release_stability_index": 0.62,
            "issue_to_commit_ratio": 1.28,
            "bus_factor_inverse": 0.5,
            "developer_load_index": 7.25,
            "commit_volatility": 0.44,
        }
        prediction = predictor.predict(features, nlp_signal_score=49.0, blend_alpha=0.82)
        risk_score = int(round(prediction.predicted_risk_score))

        mock_signals = [
            {
                "id": "fallback-1",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "message": "Fallback mode active: API rate limit or GitHub client unavailable",
                "status": "Negative",
                "source": "alert",
                "nlp": {
                    "intent": "chore",
                    "sentiment": "negative",
                    "risk_level": "medium",
                    "keywords": ["fallback", "github", "risk"],
                    "has_urgency": False,
                    "is_bug": False,
                },
            }
        ]

        return {
            "metrics": {
                "failureRiskScore": risk_score,
                "lastUpdated": datetime.utcnow().isoformat() + "Z",
                "systemHealth": self._health_from_score(risk_score),
                "metadata": {
                    "commits_30d": int(features["commits_30d"]),
                    "contributors_30d": int(features["contributors_30d"]),
                    "open_issues": int(features["open_issues"]),
                    "closed_issues_30d": int(features["closed_issues_30d"]),
                    "open_prs": int(features["open_prs"]),
                    "model_name": prediction.model_name,
                    "model_version": prediction.model_version,
                    "ml_prediction": prediction.ml_risk_score,
                    "nlp_signal_score": prediction.nlp_signal_score,
                    "blended_score": prediction.blended_risk_score,
                    "confidence": prediction.confidence,
                    "uncertainty": prediction.uncertainty,
                    "contributing_factors": prediction.contributing_factors,
                },
            },
            "signals": mock_signals,
            "temporalData": [
                {"timestamp": "6d ago", "bugGrowth": 21, "devIrregularity": 18},
                {"timestamp": "5d ago", "bugGrowth": 27, "devIrregularity": 23},
                {"timestamp": "4d ago", "bugGrowth": 32, "devIrregularity": 28},
                {"timestamp": "3d ago", "bugGrowth": 35, "devIrregularity": 31},
                {"timestamp": "2d ago", "bugGrowth": 40, "devIrregularity": 34},
                {"timestamp": "1d ago", "bugGrowth": 42, "devIrregularity": 38},
                {"timestamp": "Today", "bugGrowth": 46, "devIrregularity": 39},
            ],
            "aiInsights": {
                "title": f"Fallback analysis for {repo_name}",
                "description": f"Used fallback profile because {reason}.",
                "factors": [
                    "Synthetic repository profile used",
                    "Trained ML model still used for risk scoring",
                    "NLP signal blended into final score",
                ],
                "recommendation": "Provide valid GitHub access/token for live repository telemetry.",
                "nlp_insights": {
                    "bug_signals": 0,
                    "urgent_signals": 0,
                    "high_risk_signals": 0,
                    "positive_sentiment": 0,
                    "negative_sentiment": 1,
                    "top_keywords": ["fallback", "telemetry"],
                },
            },
            "riskBreakdown": {
                "risk_score": risk_score,
                "confidence": prediction.confidence,
                "uncertainty": prediction.uncertainty,
                "ml_risk_score": prediction.ml_risk_score,
                "nlp_signal_score": prediction.nlp_signal_score,
                "blended_risk_score": prediction.blended_risk_score,
                "reasoning_factors": prediction.contributing_factors,
            },
            "fallback": True,
            "warning": reason,
        }


def get_analyzer(github_token: str | None = None) -> GitHubAnalyzer:
    global _ANALYZER
    if github_token:
        return GitHubAnalyzer(github_token)
    if _ANALYZER is None:
        _ANALYZER = GitHubAnalyzer()
    return _ANALYZER


_ANALYZER: GitHubAnalyzer | None = None
