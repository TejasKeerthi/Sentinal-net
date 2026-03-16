"""
Sentinel-Net Backend API
FastAPI server for software reliability monitoring system
Now with NLP-powered semantic analysis, ML-driven risk prediction, and real-time WebSocket updates!
"""

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import List, Literal, Optional, Dict, Any
import random
import asyncio
import json

# Import GitHub analyzer and NLP processor
from github_analyzer import get_analyzer
from nlp_processor import get_processor, NLPAnalysis

# Import ML and Real-time modules
from ml_models import get_risk_predictor, get_anomaly_detector
from realtime_handler import get_connection_manager, get_realtime_analyzer

# ============================================================================
# Extended Data Models (Pydantic)
# ============================================================================

class SystemMetrics(BaseModel):
    """System-wide metrics"""
    failureRiskScore: int  # 0-100 (always integer, clamped)
    lastUpdated: str  # ISO format
    systemHealth: Literal["Critical", "Warning", "Nominal"]
    metadata: Optional[Dict[str, Any]] = None

class NLPMetadata(BaseModel):
    """NLP analysis metadata for signals"""
    intent: str
    sentiment: str
    risk_level: str
    keywords: List[str]
    has_urgency: bool
    is_bug: bool

class SignalItem(BaseModel):
    """Individual signal (commit, issue, alert) with optional NLP metadata"""
    id: str
    timestamp: str  # ISO format
    message: str
    status: Literal["Neutral", "Urgent", "Negative"]
    source: Literal["commit", "issue", "alert"]
    nlp: Optional[NLPMetadata] = None

class TemporalDataPoint(BaseModel):
    """Time-series data point"""
    timestamp: str
    bugGrowth: int
    devIrregularity: int

class AIInsight(BaseModel):
    """AI-generated insight"""
    title: str
    description: str
    factors: List[str]
    recommendation: str
    nlp_insights: Optional[Dict[str, Any]] = None

class SystemData(BaseModel):
    """Complete system data response"""
    metrics: SystemMetrics
    signals: List[SignalItem]
    temporalData: List[TemporalDataPoint]
    aiInsights: AIInsight

class NLPAnalysisResponse(BaseModel):
    """NLP analysis result for a single text"""
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

class MLPredictionResponse(BaseModel):
    """ML-based risk prediction response"""
    predicted_risk_score: float
    confidence_score: float
    anomaly_detected: bool
    anomaly_severity: float
    contributing_features: Dict[str, float]
    forecast_next_24h: List[float]
    timestamp: str

class AnomalyReport(BaseModel):
    """Anomaly detection report"""
    is_anomalous: bool
    severity_score: float
    anomalous_points: List[Dict[str, Any]]
    timestamp: str

# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title="Sentinel-Net API",
    description="Software Reliability Monitoring System with NLP-powered semantic analysis and Real GitHub Analysis",
    version="3.0.0"
)

# CORS Configuration - Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Mock Data (Fallback)
# ============================================================================

def get_mock_signals() -> List[SignalItem]:
    """Generate mock signals with NLP analysis"""
    nlp = get_processor()
    messages = [
        "No repository analyzed yet - enter a GitHub repo to start real analysis",
        "System initialized - NLP engine ready for semantic analysis",
        "Risk scoring algorithms loaded and calibrated",
        "Awaiting repository input for commit and issue analysis",
    ]
    
    signals = []
    status_map = ["Neutral", "Neutral", "Neutral", "Neutral"]
    source_map = ["commit", "issue", "commit", "issue"]
    
    for idx, msg in enumerate(messages, 1):
        signal_time = datetime.utcnow() - timedelta(minutes=idx*10)
        
        # Add NLP analysis
        analysis = nlp.analyze(msg)
        nlp_meta = NLPMetadata(
            intent=analysis.intent_category,
            sentiment=analysis.sentiment_label,
            risk_level=analysis.risk_level,
            keywords=analysis.keywords,
            has_urgency=analysis.has_urgency,
            is_bug=analysis.is_bug_related
        )
        
        signals.append(SignalItem(
            id=str(idx),
            timestamp=signal_time.isoformat() + "Z",
            message=msg,
            status=status_map[idx-1],
            source=source_map[idx-1],
            nlp=nlp_meta
        ))
    
    return signals

def get_mock_temporal_data() -> List[TemporalDataPoint]:
    """Generate mock temporal data"""
    return [
        {"timestamp": "00:00", "bugGrowth": 12, "devIrregularity": 8},
        {"timestamp": "04:00", "bugGrowth": 18, "devIrregularity": 12},
        {"timestamp": "08:00", "bugGrowth": 24, "devIrregularity": 15},
        {"timestamp": "12:00", "bugGrowth": 32, "devIrregularity": 22},
        {"timestamp": "16:00", "bugGrowth": 38, "devIrregularity": 28},
        {"timestamp": "20:00", "bugGrowth": 42, "devIrregularity": 32},
        {"timestamp": "24:00", "bugGrowth": 45, "devIrregularity": 35},
    ]

def get_mock_ai_insight() -> AIInsight:
    """Generate mock AI insight — placeholder until real repo is analyzed"""
    return AIInsight(
        title="Awaiting Repository Analysis",
        description="Enter a public GitHub repository to begin real analysis. The system will fetch commits, issues, and pull requests, then run NLP sentiment analysis, intent classification, and risk scoring.",
        factors=[
            "Analyze any public GitHub repository in real time",
            "NLP-powered commit message sentiment and intent analysis",
            "Automated bug detection from commit patterns",
            "Risk scoring based on issue volume, contributor activity, and code churn"
        ],
        recommendation="Start by entering a repository (e.g., TejasKeerthi/ART-VAULT) to get accurate, real signals.",
        nlp_insights={
            "bug_signals": 0,
            "urgent_signals": 0,
            "high_risk_signals": 0,
            "positive_sentiment": 0,
            "negative_sentiment": 0,
            "top_keywords": []
        }
    )

# ============================================================================
# API Endpoints - Health & System Data
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Sentinel-Net API",
        "version": "3.0.0",
        "features": ["Mock data demo", "Real GitHub analysis", "NLP semantic analysis"]
    }

@app.get("/api/system-data", response_model=SystemData)
async def get_system_data():
    """
    Get complete system data with NLP analysis
    
    Returns:
        SystemData: All metrics, signals (with NLP), temporal data, and AI insights
    """
    risk_score = 32  # Low risk for placeholder (no real repo analyzed)
    
    return SystemData(
        metrics=SystemMetrics(
            failureRiskScore=risk_score,
            lastUpdated=datetime.utcnow().isoformat() + "Z",
            systemHealth="Nominal"
        ),
        signals=get_mock_signals(),
        temporalData=get_mock_temporal_data(),
        aiInsights=get_mock_ai_insight()
    )

@app.get("/api/analyze-github")
async def analyze_github(repo: str = Query(..., description="GitHub repo (e.g., 'owner/repo' or full URL)")):
    """
    Analyze a real GitHub repository with NLP-powered semantic analysis

    Args:
        repo: GitHub repository (e.g., "torvalds/linux" or "https://github.com/torvalds/linux")

    Returns:
        SystemData: Real analysis with NLP-enhanced signals and insights

    Examples:
        /api/analyze-github?repo=torvalds/linux
        /api/analyze-github?repo=https://github.com/facebook/react
    """
    analyzer = get_analyzer()
    result = analyzer.analyze_repo(repo)

    # If it's a fallback/error
    if result.get("fallback"):
        return {
            "error": result.get("error"),
            "message": result.get("message"),
            "suggestion": "Try: /api/analyze-github?repo=torvalds/linux",
            "steps": [
                "1. Install PyGithub: pip install PyGithub",
                "2. (Optional) Get GitHub token: https://github.com/settings/tokens",
                "3. Set GITHUB_TOKEN env variable",
                "4. Try again",
            ],
        }

    # Convert to SystemData format with NLP metadata
    try:
        signals = []
        for signal_data in result.get("signals", []):
            signal = SignalItem(
                id=signal_data["id"],
                timestamp=signal_data["timestamp"],
                message=signal_data["message"],
                status=signal_data["status"],
                source=signal_data["source"],
                nlp=NLPMetadata(**signal_data["nlp"]) if signal_data.get("nlp") else None,
            )
            signals.append(signal)

        # Ensure risk score is an integer 0-100
        metrics_data = result["metrics"]
        if "failureRiskScore" in metrics_data:
            metrics_data["failureRiskScore"] = max(0, min(100, int(round(metrics_data["failureRiskScore"]))))

        ai_insights_data = result.get("aiInsights", {})
        ai_insights = AIInsight(
            title=ai_insights_data.get("title", "Analysis Complete"),
            description=ai_insights_data.get("description", ""),
            factors=ai_insights_data.get("factors", []),
            recommendation=ai_insights_data.get("recommendation", ""),
            nlp_insights=ai_insights_data.get("nlp_insights"),
        )

        return SystemData(
            metrics=SystemMetrics(**metrics_data),
            signals=signals,
            temporalData=[TemporalDataPoint(**t) for t in result.get("temporalData", [])],
            aiInsights=ai_insights,
        )
    except Exception as e:
        return {
            "error": str(e),
            "data": result,
        }

@app.get("/api/metrics", response_model=SystemMetrics)
async def get_metrics():
    """Get only system metrics"""
    risk_score = random.randint(60, 85)
    
    return SystemMetrics(
        failureRiskScore=risk_score,
        lastUpdated=datetime.utcnow().isoformat() + "Z",
        systemHealth="Warning" if risk_score > 50 else "Nominal"
    )

@app.get("/api/signals", response_model=List[SignalItem])
async def get_signals(limit: int = 20):
    """Get recent signals"""
    signals = get_mock_signals()
    return signals[:limit]

@app.get("/api/temporal-data", response_model=List[TemporalDataPoint])
async def get_temporal_data():
    """Get temporal trend data"""
    return get_mock_temporal_data()

@app.get("/api/ai-insights", response_model=AIInsight)
async def get_ai_insights():
    """Get AI-generated insights"""
    return get_mock_ai_insight()

@app.post("/api/analyze")
async def analyze():
    """
    Trigger system analysis and return updated data with NLP analysis
    """
    return await get_system_data()

# ============================================================================
# API Endpoints - GitHub Analysis
# ============================================================================

# ============================================================================
# API Endpoints - NLP Analysis
# ============================================================================

@app.post("/api/nlp/analyze", response_model=NLPAnalysisResponse)
async def nlp_analyze(text: str = Query(..., description="Text to analyze (commit message, issue, etc.)")):
    """
    Perform NLP analysis on arbitrary text
    
    Provides:
    - Sentiment analysis
    - Intent classification (bug_fix, feature, refactor, etc.)
    - Risk scoring
    - Keyword extraction
    - Bug detection
    - Urgency detection
    
    Args:
        text: Text to analyze (e.g., a commit message)
    
    Returns:
        NLPAnalysisResponse: Complete NLP analysis results
    
    Example:
        /api/nlp/analyze?text=Fixed%20critical%20memory%20leak%20in%20authentication%20module
    """
    nlp = get_processor()
    analysis = nlp.analyze(text)
    
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
        factors=analysis.factors
    )

@app.post("/api/nlp/batch-analyze")
async def nlp_batch_analyze(texts: List[str] = Query(..., description="Texts to analyze")):
    """
    Perform NLP analysis on multiple texts efficiently
    
    Args:
        texts: List of texts to analyze
    
    Returns:
        List of NLP analysis results
    
    Example:
        /api/nlp/batch-analyze?texts=Fixed%20bug&texts=Added%20feature
    """
    from nlp_processor import analyze_batch
    analyses = analyze_batch(texts)
    
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
            factors=a.factors
        )
        for a in analyses
    ]

@app.get("/api/nlp/health")
async def nlp_health():
    """Check NLP processor health and capabilities"""
    nlp = get_processor()
    return {
        "status": "healthy",
        "nlp_processor": "initialized",
        "capabilities": [
            "sentiment_analysis",
            "intent_classification",
            "risk_assessment",
            "keyword_extraction",
            "bug_detection",
            "urgency_detection"
        ],
        "intent_categories": [
            "bug_fix",
            "feature",
            "refactor",
            "docs",
            "test",
            "chore",
            "security",
            "unknown"
        ]
    }

# ============================================================================
# API Endpoints - ML Analysis & Prediction
# ============================================================================

@app.get("/api/ml/predict-risk", response_model=MLPredictionResponse)
async def ml_predict_risk(
    commits_30d: int = 10,
    contributors_30d: int = 3,
    open_issues: int = 5,
    closed_issues_30d: int = 8,
    avg_commit_frequency: float = 2.5,
    code_churn_rate: float = 0.3,
    test_coverage: float = 75.0,
    ci_failures_rate: float = 0.05
):
    """
    Predict software failure risk using Machine Learning (Random Forest + Gradient Boosting)
    
    Args:
        commits_30d: Number of commits in last 30 days
        contributors_30d: Number of contributors in last 30 days
        open_issues: Current open issues count
        closed_issues_30d: Closed issues in last 30 days
        avg_commit_frequency: Average commits per day
        code_churn_rate: Fraction of code changed per commit
        test_coverage: Percentage test coverage (0-100)
        ci_failures_rate: CI/CD failure rate (0-1)
    
    Returns:
        MLPredictionResponse: Risk prediction with confidence and 24h forecast
    """
    predictor = get_risk_predictor()
    prediction = predictor.predict_risk(
        commits_30d=commits_30d,
        contributors_30d=contributors_30d,
        open_issues=open_issues,
        closed_issues_30d=closed_issues_30d,
        avg_commit_frequency=avg_commit_frequency,
        code_churn_rate=code_churn_rate,
        test_coverage=test_coverage,
        ci_failures_rate=ci_failures_rate
    )
    
    return MLPredictionResponse(
        predicted_risk_score=prediction.predicted_risk_score,
        confidence_score=prediction.confidence_score,
        anomaly_detected=prediction.anomaly_detected,
        anomaly_severity=prediction.anomaly_severity,
        contributing_features=prediction.contributing_features,
        forecast_next_24h=prediction.forecast_next_24h,
        timestamp=prediction.timestamp
    )

@app.post("/api/ml/detect-anomalies", response_model=AnomalyReport)
async def detect_anomalies(
    temporal_data: List[Dict[str, Any]] = None,
    signal_data: List[Dict[str, Any]] = None
):
    """
    Detect anomalies in system data using Isolation Forest
    
    Args:
        temporal_data: List of temporal data points with bugGrowth and devIrregularity
        signal_data: List of signals for context
    
    Returns:
        AnomalyReport: Detected anomalies with severity scores
    """
    if temporal_data is None:
        temporal_data = get_mock_temporal_data()
    if signal_data is None:
        signal_data = [s.dict() for s in get_mock_signals()]
    
    detector = get_anomaly_detector()
    is_anomalous, severity, anomalies = detector.detect_anomalies(temporal_data, signal_data)
    
    return AnomalyReport(
        is_anomalous=is_anomalous,
        severity_score=severity,
        anomalous_points=anomalies,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )

@app.get("/api/ml/health")
async def ml_health():
    """Check ML system status and capabilities"""
    predictor = get_risk_predictor()
    detector = get_anomaly_detector()
    
    return {
        "status": "healthy",
        "ml_system": "operational",
        "models": {
            "risk_predictor": {
                "type": "Ensemble (Random Forest + Gradient Boosting)",
                "status": "loaded",
                "features": 12
            },
            "anomaly_detector": {
                "type": "Isolation Forest",
                "status": "loaded",
                "contamination": 0.1
            }
        },
        "capabilities": [
            "risk_score_prediction",
            "24h_forecasting",
            "anomaly_detection",
            "feature_importance_analysis"
        ]
    }

# ============================================================================
# WebSocket Endpoints - Real-time Updates
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time system updates
    
    Receives:
        - 'subscribe': Subscribe to real-time updates
        - 'ping': Keep-alive ping
    
    Sends:
        - analysis_complete: When analysis is done
        - alert: High-priority alerts
        - metric_update: Metric changes
        - signal: New signals detected
    """
    manager = get_connection_manager()
    client_id = f"client_{random.randint(10000, 99999)}"
    
    try:
        await manager.connect(websocket, client_id)
        
        # Send welcome message
        await manager.send_personal(websocket, {
            'type': 'connection',
            'message': 'Connected to Sentinel-Net real-time updates',
            'client_id': client_id,
            'timestamp': datetime.utcnow().isoformat() + "Z"
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data) if isinstance(data, str) else data
            
            # Handle different message types
            if message.get('type') == 'ping':
                await manager.send_personal(websocket, {
                    'type': 'pong',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                })
            
            elif message.get('type') == 'subscribe':
                await manager.send_personal(websocket, {
                    'type': 'subscribed',
                    'channels': message.get('channels', []),
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                })
    
    except WebSocketDisconnect:
        await manager.disconnect(websocket, client_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await manager.disconnect(websocket, client_id)


@app.websocket("/ws/analyze")
async def websocket_analyze_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for streaming analysis updates
    Analyze a repository and stream results in real-time
    """
    manager = get_connection_manager()
    analyzer = get_realtime_analyzer()
    client_id = f"analyzer_{random.randint(10000, 99999)}"
    
    try:
        await manager.connect(websocket, client_id)
        
        # Wait for analysis request
        data = await websocket.receive_text()
        request = json.loads(data)
        repo = request.get('repo')
        
        if not repo:
            await manager.send_personal(websocket, {
                'type': 'error',
                'message': 'Repository URL required',
                'timestamp': datetime.utcnow().isoformat() + "Z"
            })
            return
        
        # Notify analysis starting
        await manager.send_personal(websocket, {
            'type': 'analysis_started',
            'repository': repo,
            'timestamp': datetime.utcnow().isoformat() + "Z"
        })
        
        # Perform analysis
        github_analyzer = get_analyzer()
        result = github_analyzer.analyze_repo(repo)
        
        # Stream results
        if not result.get('fallback'):
            await analyzer.process_and_stream(repo, result)
        else:
            await manager.send_personal(websocket, {
                'type': 'error',
                'message': result.get('message'),
                'timestamp': datetime.utcnow().isoformat() + "Z"
            })
    
    except WebSocketDisconnect:
        await manager.disconnect(websocket, client_id)
    except Exception as e:
        print(f"WebSocket analysis error: {e}")
        try:
            await manager.send_personal(websocket, {
                'type': 'error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat() + "Z"
            })
        except:
            pass
        await manager.disconnect(websocket, client_id)



@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global error handler"""
    return {
        "error": str(exc),
        "status": "error",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
