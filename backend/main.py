"""
Sentinel-Net Backend API
FastAPI server for software reliability monitoring system
Now with NLP-powered semantic analysis and real GitHub repository analysis!
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import List, Literal, Optional, Dict, Any
import random

# Import GitHub analyzer and NLP processor
from github_analyzer import get_analyzer
from nlp_processor import get_processor, NLPAnalysis

# ============================================================================
# Extended Data Models (Pydantic)
# ============================================================================

class SystemMetrics(BaseModel):
    """System-wide metrics"""
    failureRiskScore: int  # 0-100
    lastUpdated: str  # ISO format
    systemHealth: Literal["Critical", "Warning", "Nominal"]

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
        "Critical bug detected in authentication module - fix regression in login flow",
        "Refactored database connection pooling - improved response times",
        "Memory leak detected in WebSocket handler - investigating root cause",
        "Deployed security patch for dependency vulnerability - CVE-2026-0123",
        "Unusual spike in error rates detected - correlation with increased traffic",
        "Optimized API response time from 850ms to 120ms - cache layer implementation",
    ]
    
    signals = []
    status_map = ["Urgent", "Neutral", "Negative", "Neutral", "Negative", "Neutral"]
    source_map = ["commit", "issue", "alert", "commit", "alert", "commit"]
    
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
    """Generate mock AI insight with NLP insights"""
    return AIInsight(
        title="Elevated Risk Detected",
        description="The current failure risk score of 72% indicates elevated vulnerability in production systems. NLP analysis of recent development signals reveals three primary contributing factors: increased bug fix activity (40% of commits are bug-related), negative sentiment in development messages, and critical security concerns detected in issues.",
        factors=[
            "Bug growth rate: +48% over 24 hours",
            "Development irregularity: 35% above baseline",
            "Memory leak in WebSocket handler",
            "Unresolved authentication regression",
            "Increased error rate correlation with traffic spikes",
            "Negative sentiment trend in development signals"
        ],
        recommendation="Immediate action recommended: 1) Prioritize WebSocket memory leak investigation, 2) Conduct emergency review of authentication module, 3) Implement circuit breaker for traffic spike mitigation, 4) Increase code review frequency for critical components, 5) Monitor development signal sentiment for trend changes.",
        nlp_insights={
            "bug_signals": 2,
            "urgent_signals": 1,
            "high_risk_signals": 1,
            "positive_sentiment": 2,
            "negative_sentiment": 2,
            "top_keywords": ["bug", "critical", "memory", "leak", "security"]
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
    risk_score = random.randint(60, 85)
    
    return SystemData(
        metrics=SystemMetrics(
            failureRiskScore=risk_score,
            lastUpdated=datetime.utcnow().isoformat() + "Z",
            systemHealth="Critical" if risk_score > 85 else ("Warning" if risk_score > 70 else "Nominal")
        ),
        signals=get_mock_signals(),
        temporalData=get_mock_temporal_data(),
        aiInsights=get_mock_ai_insight()
    )

@app.get("/api/analyze-github")
async def analyze_github(repo: str = Query(..., description="GitHub repo (e.g., 'owner/repo' or full URL)")):
    """
    Analyze a real GitHub repository
    
    Args:
        repo: GitHub repository (e.g., "torvalds/linux" or "https://github.com/torvalds/linux")
    
    Returns:
        Real analysis of GitHub repository: metrics, signals, trends, insights
    
    Example:
        /api/analyze-github?repo=torvalds/linux
        /api/analyze-github?repo=https://github.com/facebook/react
    """
    analyzer = get_analyzer()
    result = analyzer.analyze_repo(repo)
    
    # If it's a fallback/error, try with mock data
    if result.get("fallback"):
        return {
            "error": result.get("error"),
            "message": result.get("message"),
            "suggestion": "Try: /api/analyze-github?repo=torvalds/linux",
            "steps": [
                "1. Install PyGithub: pip install PyGithub",
                "2. (Optional) Get GitHub token: https://github.com/settings/tokens",
                "3. Set GITHUB_TOKEN env variable",
                "4. Try again"
            ]
        }
    
    # Convert to SystemData format
    try:
        return SystemData(
            metrics=SystemMetrics(**result["metrics"]),
            signals=[SignalItem(**s) for s in result["signals"]],
            temporalData=[TemporalDataPoint(**t) for t in result["temporalData"]],
            aiInsights=AIInsight(**result["aiInsights"])
        )
    except Exception as e:
        return {
            "error": str(e),
            "data": result
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

@app.get("/api/analyze-github", response_model=SystemData)
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
                "4. Try again"
            ]
        }
    
    # Convert to SystemData format with NLP metadata
    try:
        signals = []
        for s in result.get("signals", []):
            if "nlp" in s:
                signal = SignalItem(
                    id=s["id"],
                    timestamp=s["timestamp"],
                    message=s["message"],
                    status=s["status"],
                    source=s["source"],
                    nlp=NLPMetadata(**s["nlp"]) if s.get("nlp") else None
                )
            else:
                signal = SignalItem(
                    id=s["id"],
                    timestamp=s["timestamp"],
                    message=s["message"],
                    status=s["status"],
                    source=s["source"]
                )
            signals.append(signal)
        
        ai_insights_data = result.get("aiInsights", {})
        ai_insights = AIInsight(
            title=ai_insights_data.get("title", "Analysis Complete"),
            description=ai_insights_data.get("description", ""),
            factors=ai_insights_data.get("factors", []),
            recommendation=ai_insights_data.get("recommendation", ""),
            nlp_insights=ai_insights_data.get("nlp_insights")
        )
        
        return SystemData(
            metrics=SystemMetrics(**result["metrics"]),
            signals=signals,
            temporalData=[TemporalDataPoint(**t) for t in result.get("temporalData", [])],
            aiInsights=ai_insights
        )
    except Exception as e:
        return {
            "error": str(e),
            "data": result
        }

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
# Error Handlers
# ============================================================================

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
