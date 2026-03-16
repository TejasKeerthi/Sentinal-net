"""
GitHub Repository Analyzer
Analyzes real GitHub repositories and provides software reliability metrics
Now with NLP-powered semantic analysis!
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict

from ml_risk_model import get_risk_model

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
        self.risk_model = get_risk_model()
    
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
            conflict_data = self._analyze_merge_conflicts(repo)
            
            # Adjust metrics based on merge conflicts
            if conflict_data["conflict_risk_score"] > 0:
                metrics["failureRiskScore"] = min(100, 
                    int(round(metrics["failureRiskScore"] * 0.7 + conflict_data["conflict_risk_score"] * 0.3))
                )
                # Update health status based on adjusted risk
                if metrics["failureRiskScore"] > 85:
                    metrics["systemHealth"] = "Critical"
                elif metrics["failureRiskScore"] > 70:
                    metrics["systemHealth"] = "Warning"
            
            insight = self._generate_insight(repo, metrics, signals, conflict_data)
            
            return {
                "metrics": metrics,
                "signals": signals,
                "temporalData": temporal_data,
                "aiInsights": insight,
                "mergeConflicts": conflict_data,
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
        prediction = self.risk_model.predict_risk_details(
            commits_30d=commits_30d,
            contributors_30d=contributors_30d,
            open_issues=open_issues,
        )

        nlp_score = self._calculate_risk_score_nlp(
            repo,
            commits_30d,
            contributors_30d,
            open_issues,
        )

        # Blend project-specific ensemble output with NLP risk signals.
        risk_score = int(round((0.75 * prediction["risk_score"]) + (0.25 * nlp_score)))
        risk_score = max(0, min(100, risk_score))
        
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
                "prediction": prediction,
                "nlp_risk_score": nlp_score,
                "risk_model": self.risk_model.get_status(),
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
        Calculate failure risk score (0-100) using NLP analysis.
        
        Algorithm:
          - Base score: 30 (neutral starting point)
          - NLP signals from recent commits: each bug +4, each urgent +6, each high-risk +8
          - Issue-to-commit ratio: high ratio = more risk
          - Stale repo (no recent commits): big risk penalty  
          - High contributor count: slight coordination risk
          - Low activity: moderate risk
          - Clamped to integer 0-100
        """
        score = 30  # Neutral base (lower than before — we are less alarmist)
        nlp = get_processor()
        
        # Analyze recent commits for NLP risk signals
        try:
            bug_count = 0
            urgent_count = 0
            high_risk_count = 0
            positive_count = 0
            
            sampled_commits = list(repo.get_commits()[:15])  # Sample up to 15 commits
            
            for commit in sampled_commits:
                msg = commit.commit.message.split("\n")[0]
                analysis = nlp.analyze(msg)
                
                if analysis.is_bug_related:
                    bug_count += 1
                if analysis.has_urgency:
                    urgent_count += 1
                if analysis.risk_level in ["high", "critical"]:
                    high_risk_count += 1
                if analysis.sentiment_label == "positive":
                    positive_count += 1
            
            # NLP risk additions (weighted)
            if len(sampled_commits) > 0:
                bug_ratio = bug_count / len(sampled_commits)
                score += int(bug_ratio * 20)      # Up to +20 if all commits are bug fixes
                score += urgent_count * 4          # Each urgent signal = +4
                score += high_risk_count * 5       # Each high-risk = +5
                score -= int(positive_count * 1.5) # Positive signals reduce risk slightly
        except Exception:
            pass
        
        # Issue-to-commit ratio risk
        if commits > 0:
            issue_ratio = issues / max(commits, 1)
            if issue_ratio > 2.0:
                score += 15  # Many more issues than commits
            elif issue_ratio > 1.0:
                score += 8
            elif issue_ratio > 0.5:
                score += 3
        
        # Open issue volume
        if issues > 100:
            score += 12
        elif issues > 50:
            score += 8
        elif issues > 20:
            score += 4
        
        # Activity risk: no recent commits = stale/abandoned project risk
        if commits == 0:
            score += 20  # No activity in 30 days
        elif commits < 3:
            score += 10  # Very low activity
        
        # Contributor coordination risk
        if contributors > 30:
            score += 8
        elif contributors > 15:
            score += 4
        
        # Positive: active healthy project gets risk reduction
        if commits > 20 and issues < 10 and contributors >= 2:
            score -= 10  # Healthy active project
        
        # Always clamp to 0-100 integer
        return max(0, min(100, int(round(score))))

    def _calculate_risk_score(self, commits: int, contributors: int, issues: int) -> int:
        """
        Calculate failure risk score (0-100) from trained model.
        Lower is better (less risk).
        """
        return self.risk_model.predict_risk_score(
            commits_30d=commits,
            contributors_30d=contributors,
            open_issues=issues,
        )
    
    def _extract_signals(self, repo) -> List[Dict]:
        """Extract recent signals (commits, issues, PRs) with NLP analysis and conflict detection"""
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
            
            # Recent pull requests - with NLP analysis and conflict detection
            for pr in repo.get_pulls(state="open")[:2]:
                pr_text = f"{pr.title} {pr.body or ''}"
                analysis = nlp.analyze(pr_text)
                
                # Check for merge conflicts
                has_conflicts = False
                try:
                    if pr.mergeable is False or (pr.mergeable is None and self._detect_conflicts_in_diff(pr)):
                        has_conflicts = True
                except:
                    pass
                
                # Determine status
                if has_conflicts:
                    status = "Urgent"
                elif analysis.risk_level in ["high", "critical"]:
                    status = "Negative"
                elif analysis.has_urgency:
                    status = "Urgent"
                else:
                    status = "Neutral"
                
                conflict_indicator = " [MERGE CONFLICTS]" if has_conflicts else ""
                
                signals.append({
                    "id": f"pr-{pr.number}",
                    "timestamp": pr.updated_at.isoformat() + "Z",
                    "message": f"PR: {pr.title[:60]}{conflict_indicator}",
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
    
    def _analyze_merge_conflicts(self, repo) -> Dict:
        """
        Analyze merge conflicts in pull requests with high accuracy
        Returns: conflict_data with count, severity, and details
        """
        conflict_data = {
            "total_prs_checked": 0,
            "prs_with_conflicts": 0,
            "conflict_severity": "none",  # none, low, medium, high, critical
            "conflict_risk_score": 0,  # 0-100
            "conflicts_by_file_type": {},
            "conflicting_prs": [],
            "resolution_difficulty": "easy",  # easy, moderate, difficult, complex
            "metrics": {
                "avg_conflicts_per_pr": 0,
                "max_conflicts_in_single_pr": 0,
                "merge_conflict_rate": 0.0,
                "files_most_conflicted": []
            }
        }
        
        try:
            nlp = get_processor()
            prs = repo.get_pulls(state="open")
            all_conflicts = []
            
            for pr in prs:
                conflict_data["total_prs_checked"] += 1
                
                try:
                    # Check if PR has merge conflicts
                    mergeable = pr.mergeable
                    
                    if mergeable is None:
                        # GitHub is still computing mergeability, check diff
                        conflicts = self._detect_conflicts_in_diff(pr)
                    elif not mergeable:
                        conflicts = self._detect_conflicts_in_diff(pr)
                    else:
                        conflicts = []
                    
                    if conflicts:
                        conflict_data["prs_with_conflicts"] += 1
                        all_conflicts.extend(conflicts)
                        
                        # NLP analysis of PR description for resolution complexity
                        pr_text = f"{pr.title} {pr.body or ''}"
                        analysis = nlp.analyze(pr_text)
                        
                        conflicting_pr_info = {
                            "pr_number": pr.number,
                            "title": pr.title,
                            "files_count": pr.changed_files,
                            "additions": pr.additions,
                            "deletions": pr.deletions,
                            "conflict_count": len(conflicts),
                            "conflicted_files": [c["file"] for c in conflicts],
                            "updated_at": pr.updated_at.isoformat() + "Z",
                            "resolution_difficulty": self._assess_conflict_difficulty(
                                conflicts, pr, analysis
                            ),
                            "nlp_complexity": analysis.risk_level
                        }
                        conflict_data["conflicting_prs"].append(conflicting_pr_info)
                        
                except Exception as e:
                    # PR might be closed or inaccessible
                    pass
            
            # Calculate metrics
            if conflict_data["total_prs_checked"] > 0:
                conflict_data["metrics"]["merge_conflict_rate"] = round(
                    conflict_data["prs_with_conflicts"] / conflict_data["total_prs_checked"] * 100, 2
                )
            
            if conflict_data["prs_with_conflicts"] > 0:
                conflict_data["metrics"]["avg_conflicts_per_pr"] = round(
                    len(all_conflicts) / conflict_data["prs_with_conflicts"], 1
                )
            
            # Analyze file types and frequency
            file_conflicts = {}
            for conflict in all_conflicts:
                file_type = conflict["file"].split(".")[-1] if "." in conflict["file"] else "unknown"
                file_conflicts[file_type] = file_conflicts.get(file_type, 0) + 1
            
            conflict_data["conflicts_by_file_type"] = file_conflicts
            
            # Find most conflicted files
            if all_conflicts:
                file_frequency = {}
                for conflict in all_conflicts:
                    file_frequency[conflict["file"]] = file_frequency.get(conflict["file"], 0) + 1
                sorted_files = sorted(file_frequency.items(), key=lambda x: x[1], reverse=True)
                conflict_data["metrics"]["files_most_conflicted"] = [
                    {"file": f, "conflict_count": c} for f, c in sorted_files[:5]
                ]
                conflict_data["metrics"]["max_conflicts_in_single_pr"] = max(
                    [c["conflict_count"] for c in conflict_data["conflicting_prs"]], default=0
                )
            
            # Determine overall severity
            if conflict_data["prs_with_conflicts"] == 0:
                conflict_data["conflict_severity"] = "none"
                conflict_data["conflict_risk_score"] = 0
            elif conflict_data["metrics"]["merge_conflict_rate"] > 50:
                conflict_data["conflict_severity"] = "critical"
                conflict_data["conflict_risk_score"] = 95
            elif conflict_data["metrics"]["merge_conflict_rate"] > 30:
                conflict_data["conflict_severity"] = "high"
                conflict_data["conflict_risk_score"] = 75
            elif conflict_data["metrics"]["merge_conflict_rate"] > 15:
                conflict_data["conflict_severity"] = "medium"
                conflict_data["conflict_risk_score"] = 50
            else:
                conflict_data["conflict_severity"] = "low"
                conflict_data["conflict_risk_score"] = 25
            
            # Assess overall resolution difficulty
            if conflict_data["conflicting_prs"]:
                difficulties = [p["resolution_difficulty"] for p in conflict_data["conflicting_prs"]]
                difficulty_score = {"easy": 1, "moderate": 2, "difficult": 3, "complex": 4}
                avg_difficulty = sum(difficulty_score.get(d, 0) for d in difficulties) / len(difficulties)
                
                if avg_difficulty > 3:
                    conflict_data["resolution_difficulty"] = "complex"
                elif avg_difficulty > 2:
                    conflict_data["resolution_difficulty"] = "difficult"
                elif avg_difficulty > 1:
                    conflict_data["resolution_difficulty"] = "moderate"
                else:
                    conflict_data["resolution_difficulty"] = "easy"
            
        except Exception as e:
            conflict_data["error"] = str(e)
        
        return conflict_data
    
    def _detect_conflicts_in_diff(self, pr) -> List[Dict]:
        """
        Analyze PR diff to detect merge conflicts
        Returns list of conflict details
        """
        conflicts = []
        
        try:
            # Get all files in the PR
            for file_change in pr.get_files():
                conflict_markers = self._detect_conflict_markers(file_change.patch or "")
                
                if conflict_markers:
                    conflicts.append({
                        "file": file_change.filename,
                        "conflict_count": len(conflict_markers),
                        "additions": file_change.additions,
                        "deletions": file_change.deletions,
                        "changes": file_change.changes,
                        "is_binary": file_change.patch is None,
                        "conflict_markers": conflict_markers
                    })
        except Exception as e:
            pass
        
        return conflicts
    
    def _detect_conflict_markers(self, patch: str) -> List[Dict]:
        """
        Detect <<<<<<< ======= >>>>>>> conflict markers in patch text
        Returns list of conflict marker positions
        """
        markers = []
        lines = patch.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Look for opening conflict marker
            if line.startswith('<<<<<<<'):
                conflict_start = i
                separator_line = None
                end_line = None
                
                # Find separator and end markers
                for j in range(i + 1, min(i + 1000, len(lines))):  # Limit search to 1000 lines
                    if lines[j].startswith('=======') and separator_line is None:
                        separator_line = j
                    elif lines[j].startswith('>>>>>>>'):
                        end_line = j
                        break
                
                if separator_line and end_line:
                    conflict_block = {
                        "start": conflict_start,
                        "separator": separator_line,
                        "end": end_line,
                        "lines_in_conflict": end_line - conflict_start + 1,
                        "branch_a_lines": separator_line - conflict_start - 1,
                        "branch_b_lines": end_line - separator_line - 1
                    }
                    markers.append(conflict_block)
                    i = end_line
            
            i += 1
        
        return markers
    
    def _assess_conflict_difficulty(self, conflicts: List[Dict], pr, nlp_analysis) -> str:
        """
        Assess how difficult it will be to resolve these conflicts
        """
        if not conflicts:
            return "easy"
        
        # Scoring factors
        score = 0
        
        # Factor 1: Number of conflicts
        score += min(len(conflicts) * 10, 30)
        
        # Factor 2: File types involved
        risky_extensions = {'.cs', '.java', '.ts', '.tsx', '.jsx', '.py', '.cpp', '.c', '.h'}
        for conflict in conflicts:
            if any(conflict["file"].endswith(ext) for ext in risky_extensions):
                score += 5
            # Binary files are very hard to merge
            if conflict["is_binary"]:
                score += 15
        
        # Factor 3: Size of conflicts
        total_conflict_lines = sum(c.get("lines_in_conflict", 0) for c in conflicts)
        score += min(total_conflict_lines // 10, 25)
        
        # Factor 4: PR changes magnitude
        if pr.changed_files > 30:
            score += 10
        if pr.additions > 500:
            score += 5
        
        # Factor 5: NLP complexity indicator
        if nlp_analysis.risk_level in ["high", "critical"]:
            score += 10
        if nlp_analysis.has_urgency:
            score += 5
        
        # Categorize difficulty
        if score > 60:
            return "complex"
        elif score > 40:
            return "difficult"
        elif score > 20:
            return "moderate"
        else:
            return "easy"
        
        return trends
    
    def _generate_insight(self, repo, metrics: Dict, signals: List, conflict_data: Dict = None) -> Dict:
        """Generate AI insight based on NLP analysis of signals, metrics, and merge conflicts"""
        if conflict_data is None:
            conflict_data = {}
        
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
        
        # Build insight title based on findings (conflicts take priority)
        if conflict_data and conflict_data.get("prs_with_conflicts", 0) > 0:
            if conflict_data["conflict_severity"] in ["critical", "high"]:
                title = f"Critical: Merge Conflicts Blocking {conflict_data['prs_with_conflicts']} PRs"
            else:
                title = f"Attention: Merge Conflicts in Pull Requests"
        elif len(high_risk_signals) > 0:
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
        
        # Build factors from NLP + metrics + conflicts
        factors = []
        
        # Add merge conflict factors (highest priority)
        if conflict_data:
            if conflict_data.get("prs_with_conflicts", 0) > 0:
                if conflict_data["conflict_severity"] == "critical":
                    factors.append(f"🚨 CRITICAL: {conflict_data['prs_with_conflicts']} PRs with merge conflicts ({conflict_data['metrics']['merge_conflict_rate']}% conflict rate)")
                elif conflict_data["conflict_severity"] == "high":
                    factors.append(f"⚠️ HIGH: {conflict_data['prs_with_conflicts']} PRs with merge conflicts, {conflict_data['metrics']['avg_conflicts_per_pr']:.1f} avg conflicts/PR")
                elif conflict_data["conflict_severity"] == "medium":
                    factors.append(f"⚠️ MEDIUM: {conflict_data['prs_with_conflicts']} PRs with merge conflicts")
                else:
                    factors.append(f"ℹ️ LOW: {conflict_data['prs_with_conflicts']} PR with merge conflicts")
                
                # Add file type info
                if conflict_data.get('conflicts_by_file_type'):
                    file_types = [f"{ft} ({c})" for ft, c in conflict_data['conflicts_by_file_type'].items()]
                    factors.append(f"✗ Conflicts in: {', '.join(file_types)}")
                
                # Add most conflicted files
                if conflict_data.get('metrics', {}).get('files_most_conflicted'):
                    top_file = conflict_data['metrics']['files_most_conflicted'][0]
                    factors.append(f"📄 Most conflicted: {top_file['file']} ({top_file['conflict_count']} times)")
                
                # Add resolution difficulty
                factors.append(f"🔧 Resolution difficulty: {conflict_data.get('resolution_difficulty', 'unknown')}")
        
        # NLP-based factors
        if len(bug_signals) > 0:
            factors.append(f"Bug fixes detected in {len(bug_signals)} recent signals")
        
        if len(urgent_signals) > len([s for s in urgent_signals if "[MERGE CONFLICTS]" in s.get("message", "")]):
            non_conflict_urgent = len([s for s in urgent_signals if "[MERGE CONFLICTS]" not in s.get("message", "")])
            if non_conflict_urgent > 0:
                factors.append(f"Urgent items identified: {non_conflict_urgent} signals require attention")
        
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

        model_status = self.risk_model.get_status()
        prediction = metrics["metadata"].get("prediction", {})
        if model_status.get("trained"):
            factors.append(
                "ML risk model active: "
                f"{model_status.get('model')} trained on {model_status.get('augmented_samples', model_status.get('raw_samples'))} samples "
                f"(CV MAE: {model_status.get('mae_cv')}, confidence: {prediction.get('confidence', 'n/a')})"
            )
        else:
            factors.append("ML risk model unavailable; fallback heuristic scoring is active")
        
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
        
        # Generate recommendation based on all factors (merge conflicts top priority)
        recommendation = ""
        
        if conflict_data and conflict_data.get("prs_with_conflicts", 0) > 0:
            if conflict_data["conflict_severity"] in ["critical", "high"]:
                recommendation = f"🚨 URGENT ACTION REQUIRED: {conflict_data['prs_with_conflicts']} pull request(s) blocked by merge conflicts. "
                if conflict_data.get("resolution_difficulty") in ["difficult", "complex"]:
                    recommendation += "Conflicts are complex - recommend pair programming or expert code review. "
                recommendation += "Establish clear merge strategies, improve branch protection rules, and modernize CI/CD pipeline. "
            else:
                recommendation = f"Address merge conflicts in {conflict_data['prs_with_conflicts']} pull request(s). "
        
        recommendation += "Recommendations: "
        
        if len(bug_signals) > 2:
            recommendation += "Prioritize bug fixes and quality assurance testing. "
        if risk_score > 70 and not recommendation.startswith("🚨"):
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
            },
            "conflict_insights": {
                "total_prs_checked": conflict_data.get("total_prs_checked", 0),
                "prs_with_conflicts": conflict_data.get("prs_with_conflicts", 0),
                "conflict_severity": conflict_data.get("conflict_severity", "none"),
                "resolution_difficulty": conflict_data.get("resolution_difficulty", "easy"),
                "conflict_rate": conflict_data.get("metrics", {}).get("merge_conflict_rate", 0)
            } if conflict_data else None
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
