"""Sentinel-Net FastAPI backend with ML/NLP-powered reliability analysis."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from fastapi import FastAPI, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from github_analyzer import get_analyzer
from ml_models import get_anomaly_detector, get_risk_predictor
from nlp_processor import analyze_batch, get_processor
from realtime_handler import get_connection_manager, get_realtime_analyzer


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
                "Trained stacking ensemble is initialized",
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
