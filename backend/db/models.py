"""MongoDB data models with Pydantic validation."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator


# Enums for status and severity
class SignalStatus(str, Enum):
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    URGENT = "urgent"


class SignalSource(str, Enum):
    COMMIT = "commit"
    ISSUE = "issue"
    ALERT = "alert"
    METRIC = "metric"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Base models with MongoDB ObjectId support
class PyObjectId(BaseModel):
    """Custom type for MongoDB ObjectId."""
    pass


# System Risk Assessment
class RiskFactors(BaseModel):
    """Contributing factors to risk score."""
    bug_growth_rate: float = Field(..., ge=0, le=1, description="Rate of bug growth (0-1)")
    development_irregularity: float = Field(..., ge=0, le=1, description="Development pattern anomaly (0-1)")
    critical_issues: int = Field(..., ge=0, description="Number of critical issues")
    pr_velocity: float = Field(..., ge=0, description="Pull request velocity")
    test_coverage_trend: float = Field(..., ge=-1, le=1, description="Test coverage trend (-1 to 1)")
    dependency_freshness: float = Field(..., ge=0, le=1, description="How fresh dependencies are (0-1)")


class SystemRiskAssessment(BaseModel):
    """System-wide risk assessment."""
    id: Optional[str] = Field(None, alias="_id")
    failure_risk_score: int = Field(..., ge=0, le=100, description="Main risk score")
    risk_level: RiskLevel
    factors: RiskFactors
    contributing_factors: Dict[str, float] = Field(default_factory=dict)
    confidence_score: float = Field(..., ge=0, le=1)
    uncertainty_score: float = Field(..., ge=0, le=1)
    model_name: str = "sentinel-risk-model-v1"
    model_version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    analysis_duration_ms: float = Field(description="Time taken to calculate risk")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "failure_risk_score": 42,
                "risk_level": "medium",
                "factors": {
                    "bug_growth_rate": 0.15,
                    "development_irregularity": 0.25,
                    "critical_issues": 2,
                    "pr_velocity": 8.5,
                    "test_coverage_trend": 0.1,
                    "dependency_freshness": 0.7
                },
                "confidence_score": 0.92
            }
        }


# Semantic Signals/Events
class SemanticSignal(BaseModel):
    """Individual signal from repository."""
    id: Optional[str] = Field(None, alias="_id")
    source: SignalSource
    status: SignalStatus
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    severity: float = Field(..., ge=0, le=1, description="Severity score 0-1")
    nlp_score: float = Field(..., ge=0, le=1, description="NLP sentiment/anomaly score")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    repository_url: Optional[str]
    branch: Optional[str]
    commit_hash: Optional[str]
    author: Optional[str]
    pr_number: Optional[int]
    issue_number: Optional[int]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


# Temporal Metrics/Trends
class MetricDataPoint(BaseModel):
    """Single metric data point."""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TemporalTrend(BaseModel):
    """Time-series trend data."""
    id: Optional[str] = Field(None, alias="_id")
    metric_name: str = Field(..., min_length=1)
    metric_type: str = Field(..., description="e.g., 'bug_growth', 'dev_velocity'")
    data_points: List[MetricDataPoint]
    start_date: datetime
    end_date: datetime
    granularity: str = Field(default="daily", description="'hourly', 'daily', 'weekly'")
    aggregation_method: str = Field(default="mean", description="'mean', 'sum', 'max', 'min'")
    statistical_summary: Dict[str, float] = Field(
        default_factory=dict,
        description="min, max, mean, median, stddev"
    )
    repository: Optional[str]
    branch: Optional[str]
    
    class Config:
        populate_by_name = True


# AI Insights
class AIPrediction(BaseModel):
    """AI model prediction."""
    prediction_value: float
    confidence: float = Field(..., ge=0, le=1)
    contributing_factors: Dict[str, float]
    latency_ms: float


class AIInsight(BaseModel):
    """Explainable AI insight."""
    id: Optional[str] = Field(None, alias="_id")
    title: str
    description: str
    prediction: AIPrediction
    risk_factors: List[str]
    recommendations: List[str] = Field(default_factory=list)
    model_name: str
    model_version: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    confidence_interval: Dict[str, float] = Field(default_factory=dict)
    affected_components: List[str] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True


# Repository Metadata
class RepositoryMetadata(BaseModel):
    """Repository metadata for tracking."""
    id: Optional[str] = Field(None, alias="_id")
    repository_url: str
    repository_name: str
    owner: str
    branch: str = "main"
    last_analyzed: datetime = Field(default_factory=datetime.utcnow)
    analysis_frequency: str = Field(default="hourly", description="Analysis schedule")
    
    # GitHub stats (cached)
    commits_30d: int = 0
    contributors_30d: int = 0
    open_issues: int = 0
    closed_issues_30d: int = 0
    open_prs: int = 0
    average_pr_merge_time: float = 0
    
    # Configuration
    enabled: bool = True
    watch_branches: List[str] = Field(default_factory=lambda: ["main", "develop"])
    ignore_paths: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


# Analytics/Reports
class RiskReport(BaseModel):
    """Comprehensive risk report."""
    id: Optional[str] = Field(None, alias="_id")
    report_date: datetime = Field(default_factory=datetime.utcnow)
    period_start: datetime
    period_end: datetime
    repository: str
    
    # Aggregated metrics
    risk_scores: List[float] = Field(description="Risk scores over period")
    average_risk_score: float
    peak_risk_score: float
    trend: str = Field(description="'improving', 'stable', 'degrading'")
    
    # Issues summary
    total_signals: int
    critical_signals: int
    urgent_signals: int
    negative_signals: int
    resolved_signals: int
    
    # Recommendations
    key_recommendations: List[str] = Field(default_factory=list)
    action_items: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Export formats
    exported_at: Optional[datetime]
    export_format: Optional[str] = Field(None, description="'json', 'csv', 'pdf'")
    
    class Config:
        populate_by_name = True


# Audit Log
class AuditLog(BaseModel):
    """Audit trail for compliance."""
    id: Optional[str] = Field(None, alias="_id")
    action: str
    entity_type: str
    entity_id: Optional[str]
    user: Optional[str] = "system"
    changes: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str]
    status: str = Field(default="success")
    error_message: Optional[str]
    
    class Config:
        populate_by_name = True
