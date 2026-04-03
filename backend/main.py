"""Sentinel-Net FastAPI backend with ML/NLP-powered reliability analysis."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from fastapi import FastAPI, HTTPException, Query, Request, WebSocket, WebSocketDisconnect, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from motor.motor_asyncio import AsyncDatabase

from github_analyzer import get_analyzer
from ml_models import get_anomaly_detector, get_risk_predictor
from nlp_processor import analyze_batch, get_processor
from realtime_handler import get_connection_manager, get_realtime_analyzer

# MongoDB imports
from db.config import MongoDBConnection, MongoDBSettings, get_db
from db.database import Database
from db.indexes import IndexManager
from db.models import (
    SystemRiskAssessment,
    SemanticSignal,
    TemporalTrend,
    AIInsight,
    RepositoryMetadata,
    RiskReport,
    RiskFactors,
    RiskLevel,
    SignalStatus,
    SignalSource,
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class ErrorEnvelope(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None
    timestamp: str


class SystemMetadata(BaseModel):
    commits_30d: int = 0
    contributors_30d: int = 0
    open_issues: int = 0
    closed_issues_30d: Optional[int] = 0
    open_prs: Optional[int] = 0
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    ml_prediction: Optional[float] = None
    nlp_signal_score: Optional[float] = None
    blended_score: Optional[float] = None
    confidence: Optional[float] = None
    uncertainty: Optional[float] = None
    contributing_factors: Optional[Dict[str, float]] = None


class SystemMetrics(BaseModel):
    failureRiskScore: int = Field(..., ge=0, le=100)
    lastUpdated: str
    systemHealth: Literal["Critical", "Warning", "Nominal"]
    metadata: Optional[SystemMetadata] = None


class NLPMetadata(BaseModel):
    intent: str
    sentiment: str
    risk_level: str
    keywords: List[str]
    has_urgency: bool
    is_bug: bool


class SignalItem(BaseModel):
    id: str
    timestamp: str
    message: str
    status: Literal["Neutral", "Urgent", "Negative"]
    source: Literal["commit", "issue", "alert"]
    nlp: Optional[NLPMetadata] = None


class TemporalDataPoint(BaseModel):
    timestamp: str
    bugGrowth: int
    devIrregularity: int


class AIInsight(BaseModel):
    title: str
    description: str
    factors: List[str]
    recommendation: str
    nlp_insights: Optional[Dict[str, Any]] = None


class RepoInfo(BaseModel):
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    stars: Optional[int] = 0
    forks: Optional[int] = 0


class RiskBreakdown(BaseModel):
    risk_score: float
    confidence: float
    uncertainty: float
    ml_risk_score: float
    nlp_signal_score: float
    blended_risk_score: float
    reasoning_factors: Dict[str, float]


class SystemData(BaseModel):
    metrics: SystemMetrics
    signals: List[SignalItem]
    temporalData: List[TemporalDataPoint]
    aiInsights: AIInsight
    repoInfo: Optional[RepoInfo] = None
    riskBreakdown: Optional[RiskBreakdown] = None
    fallback: Optional[bool] = False
    warning: Optional[str] = None


class AnalyzeRepoRequest(BaseModel):
    repo: str = Field(..., min_length=3, max_length=200)


class AnalyzeTextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)


class AnalyzeBatchRequest(BaseModel):
    texts: List[str] = Field(..., min_length=1, max_length=100)


class NLPAnalysisResponse(BaseModel):
    text: str
    sentiment_score: float
    sentiment_label: str
    intent_category: str
    intent_confidence: float
    risk_level: str
    risk_score: float
    keywords: List[str]
    has_urgency: bool
    is_bug_related: bool
    factors: List[str]


class MLPredictRequest(BaseModel):
    commits_30d: int = Field(..., ge=0, le=100000)
    contributors_30d: int = Field(..., ge=1, le=10000)
    open_issues: int = Field(..., ge=0, le=100000)
    closed_issues_30d: int = Field(0, ge=0, le=100000)
    open_prs: int = Field(0, ge=0, le=100000)
    avg_commit_frequency: float = Field(0.0, ge=0.0, le=5000)
    code_churn_rate: float = Field(0.3, ge=0.0, le=1.0)
    bug_fix_ratio: float = Field(0.2, ge=0.0, le=1.0)
    urgent_signal_ratio: float = Field(0.1, ge=0.0, le=1.0)
    negative_sentiment_ratio: float = Field(0.1, ge=0.0, le=1.0)
    test_coverage: float = Field(75.0, ge=0.0, le=100.0)
    ci_failures_rate: float = Field(0.05, ge=0.0, le=1.0)
    mean_pr_cycle_time_hours: float = Field(24.0, ge=0.0, le=2000)
    release_stability_index: float = Field(0.7, ge=0.0, le=1.0)
    issue_to_commit_ratio: Optional[float] = Field(None, ge=0.0, le=1000.0)
    bus_factor_inverse: Optional[float] = Field(None, ge=0.0, le=2.0)
    developer_load_index: Optional[float] = Field(None, ge=0.0, le=10000.0)
    commit_volatility: float = Field(0.4, ge=0.0, le=1.0)
    nlp_signal_score: float = Field(30.0, ge=0.0, le=100.0)


class MLPredictionResponse(BaseModel):
    risk_score: float
    confidence: float
    uncertainty: float
    ml_risk_score: float
    nlp_signal_score: float
    blended_risk_score: float
    reasoning_factors: Dict[str, float]
    model_name: str
    model_version: str
    timestamp: str


class MLStatusResponse(BaseModel):
    trained: bool
    model_name: str
    model_version: str
    sample_count: int
    feature_count: int
    trained_at: str
    metrics: Dict[str, float]
    dataset_path: str


class AnomalyRequest(BaseModel):
    temporal_data: List[TemporalDataPoint] = Field(..., min_length=1)


class AnomalyResponse(BaseModel):
    is_anomalous: bool
    severity_score: float
    anomalous_points: List[Dict[str, Any]]
    timestamp: str


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------


app = FastAPI(
    title="Sentinel-Net API",
    description="Software reliability risk API powered by GitHub telemetry, NLP, and trained ML.",
    version="4.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# MongoDB Lifecycle Events
# ---------------------------------------------------------------------------


@app.on_event("startup")
async def startup_mongodb() -> None:
    """Initialize MongoDB connection on app startup."""
    try:
        print("🔄 Initializing MongoDB connection...")
        settings = MongoDBSettings()
        MongoDBConnection.initialize(settings)
        
        # Verify connection
        is_healthy = await MongoDBConnection.health_check()
        if is_healthy:
            print("✓ MongoDB connected successfully")
            
            # Create indexes
            db = await MongoDBConnection.get_async_db()
            print("🔨 Creating database indexes...")
            await IndexManager.create_all_indexes(db)
            print("✓ Indexes created successfully")
        else:
            print("⚠ MongoDB health check failed")
    except Exception as e:
        print(f"✗ MongoDB initialization error: {e}")


@app.on_event("shutdown")
async def shutdown_mongodb() -> None:
    """Close MongoDB connection on app shutdown."""
    try:
        print("🔄 Closing MongoDB connection...")
        await MongoDBConnection.close_async()
        print("✓ MongoDB connection closed")
    except Exception as e:
        print(f"✗ MongoDB shutdown error: {e}")


# Helper to get database instance for endpoints
async def get_database(db: AsyncDatabase = Depends(get_db)) -> Database:
    """Dependency for injecting Database class."""
    return Database(db)



@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    envelope = ErrorEnvelope(
        code="VALIDATION_ERROR",
        message="Request validation failed",
        details=exc.errors(),
        timestamp=datetime.utcnow().isoformat() + "Z",
    )
    return JSONResponse(status_code=422, content={"error": envelope.model_dump()})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    envelope = ErrorEnvelope(
        code="HTTP_ERROR",
        message=str(exc.detail),
        timestamp=datetime.utcnow().isoformat() + "Z",
    )
    return JSONResponse(status_code=exc.status_code, content={"error": envelope.model_dump()})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    envelope = ErrorEnvelope(
        code="INTERNAL_ERROR",
        message="Unexpected server error",
        details=str(exc),
        timestamp=datetime.utcnow().isoformat() + "Z",
    )
    return JSONResponse(status_code=500, content={"error": envelope.model_dump()})


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------


def _mock_system_data() -> SystemData:
    return SystemData(
        metrics=SystemMetrics(
            failureRiskScore=28,
            lastUpdated=datetime.utcnow().isoformat() + "Z",
            systemHealth="Nominal",
            metadata=SystemMetadata(
                commits_30d=0,
                contributors_30d=0,
                open_issues=0,
                model_name=get_risk_predictor().get_training_status()["model_name"],
                model_version=get_risk_predictor().get_training_status()["model_version"],
            ),
        ),
        signals=[
            SignalItem(
                id="init-1",
                timestamp=datetime.utcnow().isoformat() + "Z",
                message="Awaiting repository analysis input",
                status="Neutral",
                source="alert",
            )
        ],
        temporalData=[
            TemporalDataPoint(timestamp="6d ago", bugGrowth=10, devIrregularity=8),
            TemporalDataPoint(timestamp="5d ago", bugGrowth=12, devIrregularity=9),
            TemporalDataPoint(timestamp="4d ago", bugGrowth=14, devIrregularity=11),
            TemporalDataPoint(timestamp="3d ago", bugGrowth=16, devIrregularity=13),
            TemporalDataPoint(timestamp="2d ago", bugGrowth=18, devIrregularity=14),
            TemporalDataPoint(timestamp="1d ago", bugGrowth=17, devIrregularity=12),
            TemporalDataPoint(timestamp="Today", bugGrowth=19, devIrregularity=15),
        ],
        aiInsights=AIInsight(
            title="Awaiting Repository Analysis",
            description="Submit an owner/repo input to run live GitHub + NLP + ML risk analysis.",
            factors=[
                "Trained dual-head adaptive fusion model is initialized",
                "NLP engine is initialized",
                "System ready for repository scoring",
            ],
            recommendation="Analyze a repository (e.g., owner/repo) to generate live risk signals.",
            nlp_insights={
                "bug_signals": 0,
                "urgent_signals": 0,
                "high_risk_signals": 0,
                "positive_sentiment": 0,
                "negative_sentiment": 0,
                "top_keywords": [],
            },
        ),
    )


# ---------------------------------------------------------------------------
# Health and system endpoints
# ---------------------------------------------------------------------------


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "Sentinel-Net API",
        "version": "4.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/api/health")
async def api_health() -> Dict[str, Any]:
    ml_status = get_risk_predictor().get_training_status()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "components": {
            "github_analyzer": "ready",
            "nlp_processor": "ready",
            "ml_predictor": "ready" if ml_status.get("trained") else "degraded",
        },
        "ml": ml_status,
    }


@app.get("/api/system-data", response_model=SystemData)
async def get_system_data() -> SystemData:
    return _mock_system_data()


# ---------------------------------------------------------------------------
# Repository analysis endpoints
# ---------------------------------------------------------------------------


@app.get("/api/analyze-github", response_model=SystemData)
async def analyze_github(repo: str = Query(..., min_length=3, max_length=200)) -> SystemData:
    analyzer = get_analyzer()
    result = analyzer.analyze_repo(repo)
    return SystemData.model_validate(result)


@app.post("/api/repository/analyze", response_model=SystemData)
async def analyze_repository(payload: AnalyzeRepoRequest) -> SystemData:
    analyzer = get_analyzer()
    result = analyzer.analyze_repo(payload.repo)
    return SystemData.model_validate(result)


# ---------------------------------------------------------------------------
# NLP endpoints
# ---------------------------------------------------------------------------


@app.post("/api/nlp/analyze", response_model=NLPAnalysisResponse)
async def nlp_analyze(payload: AnalyzeTextRequest) -> NLPAnalysisResponse:
    nlp = get_processor()
    analysis = nlp.analyze(payload.text)
    return NLPAnalysisResponse(
        text=analysis.text,
        sentiment_score=analysis.sentiment_score,
        sentiment_label=analysis.sentiment_label,
        intent_category=analysis.intent_category,
        intent_confidence=analysis.intent_confidence,
        risk_level=analysis.risk_level,
        risk_score=analysis.risk_score,
        keywords=analysis.keywords,
        has_urgency=analysis.has_urgency,
        is_bug_related=analysis.is_bug_related,
        factors=analysis.factors,
    )


@app.post("/api/nlp/batch-analyze", response_model=List[NLPAnalysisResponse])
async def nlp_batch(payload: AnalyzeBatchRequest) -> List[NLPAnalysisResponse]:
    analyses = analyze_batch(payload.texts)
    return [
        NLPAnalysisResponse(
            text=a.text,
            sentiment_score=a.sentiment_score,
            sentiment_label=a.sentiment_label,
            intent_category=a.intent_category,
            intent_confidence=a.intent_confidence,
            risk_level=a.risk_level,
            risk_score=a.risk_score,
            keywords=a.keywords,
            has_urgency=a.has_urgency,
            is_bug_related=a.is_bug_related,
            factors=a.factors,
        )
        for a in analyses
    ]


@app.get("/api/nlp/health")
async def nlp_health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "capabilities": [
            "sentiment_analysis",
            "intent_classification",
            "risk_assessment",
            "keyword_extraction",
            "urgency_detection",
        ],
    }


# ---------------------------------------------------------------------------
# ML endpoints
# ---------------------------------------------------------------------------


@app.get("/api/ml/status", response_model=MLStatusResponse)
async def ml_status() -> MLStatusResponse:
    return MLStatusResponse.model_validate(get_risk_predictor().get_training_status())


@app.post("/api/ml/predict", response_model=MLPredictionResponse)
async def ml_predict(payload: MLPredictRequest) -> MLPredictionResponse:
    predictor = get_risk_predictor()

    feature_payload = payload.model_dump()
    nlp_signal_score = feature_payload.pop("nlp_signal_score")

    if feature_payload.get("issue_to_commit_ratio") is None:
        feature_payload["issue_to_commit_ratio"] = feature_payload["open_issues"] / max(feature_payload["commits_30d"], 1)
    if feature_payload.get("bus_factor_inverse") is None:
        feature_payload["bus_factor_inverse"] = 1 / max(feature_payload["contributors_30d"] ** 0.5, 1.0)
    if feature_payload.get("developer_load_index") is None:
        feature_payload["developer_load_index"] = (
            feature_payload["open_issues"] + feature_payload["open_prs"]
        ) / max(feature_payload["contributors_30d"], 1)

    prediction = predictor.predict(feature_payload=feature_payload, nlp_signal_score=nlp_signal_score)

    return MLPredictionResponse(
        risk_score=prediction.predicted_risk_score,
        confidence=prediction.confidence,
        uncertainty=prediction.uncertainty,
        ml_risk_score=prediction.ml_risk_score,
        nlp_signal_score=prediction.nlp_signal_score,
        blended_risk_score=prediction.blended_risk_score,
        reasoning_factors=prediction.contributing_factors,
        model_name=prediction.model_name,
        model_version=prediction.model_version,
        timestamp=prediction.timestamp,
    )


@app.post("/api/ml/detect-anomalies", response_model=AnomalyResponse)
async def detect_anomalies(payload: AnomalyRequest) -> AnomalyResponse:
    detector = get_anomaly_detector()
    data = [item.model_dump() for item in payload.temporal_data]
    is_anomalous, severity, anomalies = detector.detect_anomalies(data)
    return AnomalyResponse(
        is_anomalous=is_anomalous,
        severity_score=severity,
        anomalous_points=anomalies,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


# ---------------------------------------------------------------------------
# MongoDB Database Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/db/health")
async def db_health(db: Database = Depends(get_database)) -> Dict[str, Any]:
    """Check MongoDB connection health."""
    is_healthy = await MongoDBConnection.health_check()
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "database": MongoDBConnection._settings.mongodb_database if MongoDBConnection._settings else "unknown",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/api/db/risk-assessment/save")
async def save_risk_assessment(
    assessment: SystemRiskAssessment,
    db: Database = Depends(get_database),
) -> Dict[str, str]:
    """Save risk assessment to MongoDB."""
    try:
        assessment_id = await db.save_risk_assessment(assessment)
        await db.log_action(
            action="CREATE",
            entity_type="RiskAssessment",
            entity_id=assessment_id,
        )
        return {"id": assessment_id, "status": "saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save assessment: {str(e)}")


@app.get("/api/db/risk-assessment/latest")
async def get_latest_risk_assessment(
    db: Database = Depends(get_database),
) -> Optional[Dict[str, Any]]:
    """Get latest risk assessment."""
    assessment = await db.get_latest_risk_assessment()
    if assessment:
        return assessment.model_dump(by_alias=True)
    return None


@app.get("/api/db/risk-assessment/history")
async def get_risk_history(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(100, ge=1, le=1000),
    db: Database = Depends(get_database),
) -> List[Dict[str, Any]]:
    """Get risk assessment history."""
    assessments = await db.get_risk_assessment_history(days=days, limit=limit)
    return [a.model_dump(by_alias=True) for a in assessments]


@app.get("/api/db/risk-assessment/statistics")
async def get_risk_statistics(
    days: int = Query(30, ge=1, le=365),
    db: Database = Depends(get_database),
) -> Dict[str, Any]:
    """Get risk statistics over period."""
    return await db.get_risk_statistics(days=days)


@app.post("/api/db/signal/save")
async def save_signal(
    signal: SemanticSignal,
    db: Database = Depends(get_database),
) -> Dict[str, str]:
    """Save semantic signal to MongoDB."""
    try:
        signal_id = await db.save_signal(signal)
        await db.log_action(
            action="CREATE",
            entity_type="Signal",
            entity_id=signal_id,
        )
        return {"id": signal_id, "status": "saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save signal: {str(e)}")


@app.get("/api/db/signals")
async def get_signals(
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0),
    db: Database = Depends(get_database),
) -> Dict[str, Any]:
    """Get signals with filtering and pagination."""
    signals = await db.get_signals(status=status, source=source, limit=limit, skip=skip)
    aggregated = await db.get_signals_aggregated()
    return {
        "data": [s.model_dump(by_alias=True) for s in signals],
        "count": len(signals),
        "summary": aggregated,
    }


@app.post("/api/db/signals/bulk")
async def bulk_insert_signals(
    signals: List[SemanticSignal],
    db: Database = Depends(get_database),
) -> Dict[str, int]:
    """Bulk insert multiple signals."""
    if not signals:
        raise HTTPException(status_code=400, detail="No signals provided")
    
    count = await db.bulk_insert_signals(signals)
    return {"inserted_count": count}


@app.get("/api/db/signals/search")
async def search_signals(
    query: str = Query(..., min_length=3),
    limit: int = Query(20, ge=1, le=100),
    db: Database = Depends(get_database),
) -> Dict[str, Any]:
    """Full-text search on signals."""
    signals = await db.search_signals(query, limit=limit)
    return {
        "query": query,
        "results": [s.model_dump(by_alias=True) for s in signals],
        "count": len(signals),
    }


@app.post("/api/db/trend/save")
async def save_trend(
    trend: TemporalTrend,
    db: Database = Depends(get_database),
) -> Dict[str, str]:
    """Save temporal trend to MongoDB."""
    try:
        trend_id = await db.save_trend(trend)
        await db.log_action(
            action="CREATE",
            entity_type="Trend",
            entity_id=trend_id,
        )
        return {"id": trend_id, "status": "saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save trend: {str(e)}")


@app.get("/api/db/trend/{metric_name}")
async def get_trend(
    metric_name: str,
    db: Database = Depends(get_database),
) -> Optional[Dict[str, Any]]:
    """Get latest trend for metric."""
    trend = await db.get_trend(metric_name)
    if trend:
        return trend.model_dump(by_alias=True)
    return None


@app.get("/api/db/trends/comparison")
async def compare_trends(
    metrics: str = Query(..., description="Comma-separated metric names"),
    days: int = Query(30, ge=1, le=365),
    db: Database = Depends(get_database),
) -> List[Dict[str, Any]]:
    """Compare multiple trends."""
    metric_list = [m.strip() for m in metrics.split(",")]
    return await db.get_trend_comparison(metric_list, days=days)


@app.post("/api/db/ai-insight/save")
async def save_ai_insight(
    insight: AIInsight,
    db: Database = Depends(get_database),
) -> Dict[str, str]:
    """Save AI insight to MongoDB."""
    try:
        insight_id = await db.save_ai_insight(insight)
        await db.log_action(
            action="CREATE",
            entity_type="AIInsight",
            entity_id=insight_id,
        )
        return {"id": insight_id, "status": "saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save insight: {str(e)}")


@app.get("/api/db/ai-insights")
async def get_ai_insights(
    limit: int = Query(5, ge=1, le=50),
    db: Database = Depends(get_database),
) -> Dict[str, Any]:
    """Get latest AI insights."""
    insights = await db.get_latest_ai_insights(limit=limit)
    return {
        "insights": [i.model_dump(by_alias=True) for i in insights],
        "count": len(insights),
    }


@app.post("/api/db/repository/save")
async def save_repository(
    repo: RepositoryMetadata,
    db: Database = Depends(get_database),
) -> Dict[str, str]:
    """Save or update repository metadata."""
    try:
        repo_id = await db.save_repository(repo)
        await db.log_action(
            action="UPSERT",
            entity_type="Repository",
            entity_id=repo_id,
        )
        return {"id": repo_id, "status": "saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save repository: {str(e)}")


@app.get("/api/db/repository/{repo_url}")
async def get_repository(
    repo_url: str,
    db: Database = Depends(get_database),
) -> Optional[Dict[str, Any]]:
    """Get repository metadata."""
    repo = await db.get_repository(repo_url)
    if repo:
        return repo.model_dump(by_alias=True)
    return None


@app.post("/api/db/risk-report/save")
async def save_risk_report(
    report: RiskReport,
    db: Database = Depends(get_database),
) -> Dict[str, str]:
    """Save risk report to MongoDB."""
    try:
        report_id = await db.save_risk_report(report)
        await db.log_action(
            action="CREATE",
            entity_type="RiskReport",
            entity_id=report_id,
        )
        return {"id": report_id, "status": "saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save report: {str(e)}")


@app.get("/api/db/risk-reports")
async def get_risk_reports(
    repository: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    db: Database = Depends(get_database),
) -> Dict[str, Any]:
    """Get risk reports."""
    reports = await db.get_risk_reports(repository=repository, limit=limit)
    return {
        "reports": [r.model_dump(by_alias=True) for r in reports],
        "count": len(reports),
    }


@app.get("/api/db/dashboard/summary")
async def get_dashboard_summary(
    db: Database = Depends(get_database),
) -> Dict[str, Any]:
    """Get comprehensive dashboard summary."""
    return await db.get_dashboard_summary()


@app.get("/api/db/audit-logs")
async def get_audit_logs(
    action: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(100, ge=1, le=1000),
    db: Database = Depends(get_database),
) -> Dict[str, Any]:
    """Get audit logs."""
    logs = await db.get_audit_logs(action=action, days=days, limit=limit)
    return {
        "logs": [l.model_dump(by_alias=True) for l in logs],
        "count": len(logs),
    }


@app.delete("/api/db/cleanup")
async def cleanup_old_data(
    days: int = Query(90, ge=7, le=365, description="Delete data older than X days"),
    db: Database = Depends(get_database),
) -> Dict[str, Any]:
    """Clean up old signals (maintenance endpoint)."""
    deleted_count = await db.delete_old_signals(days=days)
    await db.log_action(
        action="CLEANUP",
        entity_type="DataMaintenance",
        changes={"deleted_signals": deleted_count, "older_than_days": days},
    )
    return {
        "deleted_count": deleted_count,
        "older_than_days": days,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ---------------------------------------------------------------------------
# WebSocket endpoints
# ---------------------------------------------------------------------------


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    manager = get_connection_manager()
    client_id = f"client-{int(datetime.utcnow().timestamp() * 1000)}"
    await manager.connect(websocket, client_id)

    try:
        await manager.send_personal(
            websocket,
            {
                "type": "connection",
                "client_id": client_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        )

        while True:
            _ = await websocket.receive_text()
            await manager.send_personal(
                websocket,
                {
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                },
            )
    except WebSocketDisconnect:
        await manager.disconnect(websocket, client_id)


@app.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket) -> None:
    manager = get_connection_manager()
    realtime = get_realtime_analyzer()
    analyzer = get_analyzer()

    client_id = f"analyzer-{int(datetime.utcnow().timestamp() * 1000)}"
    await manager.connect(websocket, client_id)

    try:
        raw = await websocket.receive_json()
        repo = raw.get("repo")
        if not repo:
            await manager.send_personal(
                websocket,
                {
                    "type": "error",
                    "message": "Repository URL required",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                },
            )
            return

        await manager.send_personal(
            websocket,
            {
                "type": "analysis_started",
                "repository": repo,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        )

        result = analyzer.analyze_repo(repo)
        await realtime.process_and_stream(repo, result)

    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(websocket, client_id)


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=False)
