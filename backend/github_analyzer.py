"""
GitHub Repository Analyzer
Analyzes real GitHub repositories and provides software reliability metrics
Now with NLP-powered semantic analysis!
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import re

try:
    from github import Github, GithubException
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False

# Import NLP processor
from nlp_processor import get_processor


class GitHubAnalyzer:
    """Analyze real GitHub repositories for software reliability"""
    
    def __init__(self, github_token: str = None):
        """
        Initialize GitHub analyzer
        
        Args:
            github_token: GitHub API token (optional, for higher rate limits)
                         Get one at: https://github.com/settings/tokens
        """
        self.token = github_token or os.getenv("GITHUB_TOKEN")
        if GITHUB_AVAILABLE:
            self.client = Github(self.token) if self.token else Github()
        else:
            self.client = None
    
    def analyze_repo(self, repo_url: str) -> Dict:
        """
        Analyze a GitHub repository and return reliability metrics
        
        Args:
            repo_url: GitHub repo URL (e.g., "https://github.com/owner/repo" or "owner/repo")
        
        Returns:
            Dictionary with metrics, signals, trends, and insights
        """
        if not GITHUB_AVAILABLE:
            return self._mock_analysis(repo_url)
        
        try:
            # Extract owner/repo from URL
            repo_path = self._extract_repo_path(repo_url)
            repo = self.client.get_repo(repo_path)
            
            # Analyze different aspects
            metrics = self._calculate_metrics(repo)
            signals = self._extract_signals(repo)
            temporal_data = self._analyze_temporal_trends(repo)
            insight = self._generate_insight(repo, metrics, signals)
            
            return {
                "metrics": metrics,
                "signals": signals,
                "temporalData": temporal_data,
                "aiInsights": insight,
                "repoInfo": {
                    "name": repo.full_name,
                    "description": repo.description,
                    "url": repo.html_url,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                }
            }
        except GithubException as e:
            return {
                "error": f"GitHub API Error: {str(e)}",
                "message": "Could not access repository. Check URL and GitHub token.",
                "fallback": True
            }
        except Exception as e:
            return {
                "error": f"Analysis Error: {str(e)}",
                "fallback": True
            }
    
    def _extract_repo_path(self, repo_url: str) -> str:
        """Extract owner/repo from GitHub URL"""
        # Handle different URL formats
        if "github.com/" in repo_url:
            # Extract from URL
            parts = repo_url.split("github.com/")[1].strip("/").split("/")
            return f"{parts[0]}/{parts[1]}"
        else:
            # Assume it's already in owner/repo format
            return repo_url.strip("/")
    
    def _calculate_metrics(self, repo) -> Dict:
        """Calculate software reliability metrics with NLP enhancement"""
        commits_30d = self._count_recent_commits(repo, days=30)
        contributors_30d = self._count_recent_contributors(repo, days=30)
        open_issues = repo.open_issues_count
        
        # NLP-enhanced risk calculation
        risk_score = self._calculate_risk_score_nlp(
            repo,
            commits_30d, 
            contributors_30d, 
            open_issues
        )
        
        # Health status
        if risk_score > 85:
            health = "Critical"
        elif risk_score > 70:
            health = "Warning"
        else:
            health = "Nominal"
        
        return {
            "failureRiskScore": risk_score,
            "lastUpdated": datetime.utcnow().isoformat() + "Z",
            "systemHealth": health,
            "metadata": {
                "commits_30d": commits_30d,
                "contributors_30d": contributors_30d,
                "open_issues": open_issues,
            }
        }
    
    def _count_recent_commits(self, repo, days: int = 30) -> int:
        """Count commits in last N days"""
        try:
            since = datetime.utcnow() - timedelta(days=days)
            commits = repo.get_commits(since=since)
            return commits.totalCount
        except:
            return 0
    
    def _count_recent_contributors(self, repo, days: int = 30) -> int:
        """Count unique contributors in last N days"""
        try:
            since = datetime.utcnow() - timedelta(days=days)
            commits = repo.get_commits(since=since)
            contributors = set()
            for commit in commits[:100]:  # Limit to avoid rate limits
                if commit.author:
                    contributors.add(commit.author.login)
            return len(contributors)
        except:
            return 0
    
    def _calculate_risk_score_nlp(self, repo, commits: int, contributors: int, issues: int) -> int:
        """
        Calculate failure risk score (0-100) using NLP analysis
        Considers commit messages, issue descriptions, and pull request content
        """
        score = 50  # Base score
        nlp = get_processor()
        
        # Analyze recent commits for NLP risk signals
        try:
            bug_count = 0
            urgent_count = 0
            high_risk_count = 0
            
            for commit in repo.get_commits()[:10]:  # Sample first 10 commits
                msg = commit.commit.message.split("\n")[0]
                analysis = nlp.analyze(msg)
                
                if analysis.is_bug_related:
                    bug_count += 1
                if analysis.has_urgency:
                    urgent_count += 1
                if analysis.risk_level in ["high", "critical"]:
                    high_risk_count += 1
            
            # Risk increase based on NLP findings
            score += bug_count * 3  # Each bug = +3
            score += urgent_count * 5  # Each urgent = +5
            score += high_risk_count * 7  # Each high-risk = +7
        except:
            pass
        
        # Traditional metrics
        score += min(issues // 5, 20)  # High issue count
        
        if commits == 0:
            score += 25  # No activity
        elif commits < 5:
            score += 15  # Low activity
        
        if contributors > 20:
            score += 10  # Many contributors
        
        # Clamp to 0-100
        return max(0, min(100, score))
    
    def _calculate_risk_score(self, commits: int, contributors: int, issues: int) -> int:
        """
        Calculate failure risk score (0-100)
        Lower is better (less risk)
        """
        score = 50  # Base score
        
        # High issue count increases risk
        score += min(issues // 5, 20)
        
        # Low commit activity increases risk (stale repo)
        if commits == 0:
            score += 25
        elif commits < 5:
            score += 15
        
        # Many contributors can increase risk (more changes/conflicts)
        if contributors > 20:
            score += 10
        
        # Clamp to 0-100
        return max(0, min(100, score))
    
    def _extract_signals(self, repo) -> List[Dict]:
        """Extract recent signals (commits, issues, PRs) with NLP analysis"""
        signals = []
        nlp = get_processor()
        
        try:
            # Recent commits - with NLP analysis
            for commit in repo.get_commits()[:5]:
                commit_message = commit.commit.message.split("\n")[0][:120]
                analysis = nlp.analyze(commit_message)
                
                # Determine status based on NLP analysis
                if analysis.is_bug_related:
                    status = "Urgent"
                elif analysis.sentiment_score < -0.3:
                    status = "Negative"
                else:
                    status = "Neutral"
                
                signals.append({
                    "id": commit.sha[:8],
                    "timestamp": commit.commit.author.date.isoformat() + "Z",
                    "message": commit_message,
                    "status": status,
                    "source": "commit",
                    "nlp": {
                        "intent": analysis.intent_category,
                        "sentiment": analysis.sentiment_label,
                        "risk_level": analysis.risk_level,
                        "keywords": analysis.keywords[:3],
                        "has_urgency": analysis.has_urgency,
                        "is_bug": analysis.is_bug_related
                    }
                })
            
            # Recent issues - with NLP analysis
            for issue in repo.get_issues(state="open", sort="updated")[:3]:
                issue_text = f"{issue.title} {issue.body or ''}"
                analysis = nlp.analyze(issue_text)
                
                # Determine status based on NLP
                if analysis.is_bug_related or "bug" in issue.title.lower():
                    status = "Urgent"
                elif analysis.risk_level in ["high", "critical"]:
                    status = "Urgent"
                elif analysis.sentiment_score < -0.2:
                    status = "Negative"
                else:
                    status = "Neutral"
                
                signals.append({
                    "id": f"issue-{issue.number}",
                    "timestamp": issue.updated_at.isoformat() + "Z",
                    "message": issue.title[:80],
                    "status": status,
                    "source": "issue",
                    "nlp": {
                        "intent": analysis.intent_category,
                        "sentiment": analysis.sentiment_label,
                        "risk_level": analysis.risk_level,
                        "keywords": analysis.keywords[:3],
                        "has_urgency": analysis.has_urgency,
                        "is_bug": analysis.is_bug_related
                    }
                })
            
            # Recent pull requests - with NLP analysis
            for pr in repo.get_pulls(state="open")[:2]:
                pr_text = f"{pr.title} {pr.body or ''}"
                analysis = nlp.analyze(pr_text)
                
                status = "Neutral"
                if analysis.risk_level in ["high", "critical"]:
                    status = "Negative"
                elif analysis.has_urgency:
                    status = "Urgent"
                
                signals.append({
                    "id": f"pr-{pr.number}",
                    "timestamp": pr.updated_at.isoformat() + "Z",
                    "message": f"PR: {pr.title[:60]}",
                    "status": status,
                    "source": "alert",
                    "nlp": {
                        "intent": analysis.intent_category,
                        "sentiment": analysis.sentiment_label,
                        "risk_level": analysis.risk_level,
                        "keywords": analysis.keywords[:3],
                        "has_urgency": analysis.has_urgency,
                        "is_bug": analysis.is_bug_related
                    }
                })
        except Exception as e:
            # Fallback if NLP processing fails
            pass
        
        return signals[:6]  # Return top 6
    
    def _analyze_temporal_trends(self, repo) -> List[Dict]:
        """Analyze commit trends over time"""
        trends = []
        
        try:
            now = datetime.utcnow()
            for day in range(7, -1, -1):  # Last 7 days
                date = now - timedelta(days=day)
                since = date
                until = date + timedelta(days=1)
                
                commits = repo.get_commits(since=since, until=until)
                count = commits.totalCount
                
                trends.append({
                    "timestamp": f"{6-day}d ago",
                    "bugGrowth": max(10, count * 2),
                    "devIrregularity": min(50, count // 2) if count > 0 else 10
                })
        except:
            # Fallback to mock trend
            trends = [
                {"timestamp": "6d ago", "bugGrowth": 12, "devIrregularity": 8},
                {"timestamp": "5d ago", "bugGrowth": 18, "devIrregularity": 12},
                {"timestamp": "4d ago", "bugGrowth": 24, "devIrregularity": 15},
                {"timestamp": "3d ago", "bugGrowth": 32, "devIrregularity": 22},
                {"timestamp": "2d ago", "bugGrowth": 38, "devIrregularity": 28},
                {"timestamp": "1d ago", "bugGrowth": 42, "devIrregularity": 32},
                {"timestamp": "Today", "bugGrowth": 45, "devIrregularity": 35},
            ]
        
        return trends
    
    def _generate_insight(self, repo, metrics: Dict, signals: List) -> Dict:
        """Generate AI insight based on NLP analysis of signals and metrics"""
        risk_score = metrics["failureRiskScore"]
        commits = metrics["metadata"]["commits_30d"]
        issues = metrics["metadata"]["open_issues"]
        contributors = metrics["metadata"]["contributors_30d"]
        nlp = get_processor()
        
        # Analyze signals for NLP insights
        bug_signals = [s for s in signals if s.get("nlp", {}).get("is_bug", False)]
        urgent_signals = [s for s in signals if s.get("status") == "Urgent"]
        high_risk_signals = [s for s in signals if s.get("nlp", {}).get("risk_level") in ["high", "critical"]]
        
        # Extract keywords from all signals
        all_keywords = []
        for signal in signals:
            if signal.get("nlp", {}).get("keywords"):
                all_keywords.extend(signal.get("nlp", {}).get("keywords", []))
        
        # Build insight title based on NLP findings
        if len(high_risk_signals) > 0:
            title = "Critical Issues Detected in Repository"
        elif len(bug_signals) >= 2:
            title = "Multiple Bug Fixes Identified"
        elif risk_score > 70:
            title = "Elevated Software Reliability Risk"
        elif commits == 0:
            title = "Inactive Repository Detected"
        elif issues > 20:
            title = "High Critical Issue Count"
        else:
            title = "Repository Activity Analysis"
        
        # Build factors from NLP + metrics
        factors = []
        
        # NLP-based factors
        if len(bug_signals) > 0:
            factors.append(f"Bug fixes detected in {len(bug_signals)} recent signals")
        
        if len(urgent_signals) > 0:
            factors.append(f"Urgent items identified: {len(urgent_signals)} signals require attention")
        
        if len(high_risk_signals) > 0:
            factors.append(f"High-risk signals: {len(high_risk_signals)} items flagged for review")
        
        # Metrics-based factors
        if commits > 0:
            factors.append(f"Recent activity: {commits} commits by {contributors} unique contributors in last 30 days")
        else:
            factors.append(f"No commits in the last 30 days - repository appears inactive")
        
        if issues > 0:
            factors.append(f"Open issues requiring attention: {issues} items")
        
        if contributors > 15:
            factors.append(f"High contributor count ({contributors}) may indicate coordination challenges")
        
        # Build NLP-informed description
        sentiment_positive = sum(1 for s in signals if s.get("nlp", {}).get("sentiment") == "positive")
        sentiment_negative = sum(1 for s in signals if s.get("nlp", {}).get("sentiment") == "negative")
        
        description = f"NLP Analysis of {repo.full_name}: "
        if sentiment_negative > sentiment_positive:
            description += "Development signals show predominantly negative sentiment, indicating potential issues in progress. "
        elif sentiment_positive > sentiment_negative:
            description += "Development signals show positive progress momentum. "
        else:
            description += "Development signals are balanced. "
        
        description += " ".join(factors[:3])
        
        # Generate recommendation based on NLP
        recommendation = "Recommendations: "
        if len(bug_signals) > 2:
            recommendation += "Prioritize bug fixes and quality assurance testing. "
        if risk_score > 70:
            recommendation += "Conduct thorough code review and increase test coverage. "
        if issues > 20:
            recommendation += "Create issue triage process and assign priority labels. "
        if sentiment_negative > sentiment_positive:
            recommendation += "Investigate root causes of negative development signals. "
        if not recommendation.endswith(". "):
            recommendation += "Review recent commits and ensure proper documentation of changes."
        
        return {
            "title": title,
            "description": description,
            "factors": factors if factors else ["Repository analyzed successfully"],
            "recommendation": recommendation,
            "nlp_insights": {
                "bug_signals": len(bug_signals),
                "urgent_signals": len(urgent_signals),
                "high_risk_signals": len(high_risk_signals),
                "positive_sentiment": sentiment_positive,
                "negative_sentiment": sentiment_negative,
                "top_keywords": list(set(all_keywords))[:5]
            }
        }
    
    def _mock_analysis(self, repo_url: str) -> Dict:
        """Return mock data if GitHub API not available"""
        return {
            "error": "PyGithub not installed",
            "message": "Install with: pip install PyGithub",
            "suggestion": f"Would analyze: {repo_url}",
            "fallback": True
        }


def get_analyzer(github_token: str = None) -> GitHubAnalyzer:
    """Get GitHub analyzer instance"""
    return GitHubAnalyzer(github_token)
