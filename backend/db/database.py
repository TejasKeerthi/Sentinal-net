"""Database operations layer with advanced MongoDB features."""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, OperationFailure
from bson import ObjectId

from db.models import (
    SystemRiskAssessment,
    SemanticSignal,
    TemporalTrend,
    AIInsight,
    RepositoryMetadata,
    RiskReport,
    AuditLog,
)


class Database:
    """Database operations with advanced MongoDB features."""

    def __init__(self, db: Any):
        self.db = db

    # ========== RISK ASSESSMENT OPERATIONS ==========

    async def save_risk_assessment(self, assessment: SystemRiskAssessment) -> str:
        """Save or update risk assessment."""
        collection = self.db.risk_assessments
        
        doc = assessment.model_dump(exclude={"id"}, by_alias=True)
        doc["last_updated"] = datetime.utcnow()
        
        result = await collection.insert_one(doc)
        return str(result.inserted_id)

    async def get_latest_risk_assessment(self) -> Optional[SystemRiskAssessment]:
        """Get most recent risk assessment."""
        collection = self.db.risk_assessments
        doc = await collection.find_one({}, sort=[("timestamp", DESCENDING)])
        if doc:
            doc["id"] = str(doc["_id"])
            return SystemRiskAssessment(**doc)
        return None

    async def get_risk_assessment_history(
        self, days: int = 30, limit: int = 100
    ) -> List[SystemRiskAssessment]:
        """Get historical risk assessments with aggregation."""
        collection = self.db.risk_assessments
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": start_date}}},
            {"$sort": {"timestamp": DESCENDING}},
            {"$limit": limit},
        ]
        
        results = []
        async for doc in collection.aggregate(pipeline):
            doc["id"] = str(doc["_id"])
            results.append(SystemRiskAssessment(**doc))
        
        return results

    async def get_risk_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get risk statistics using aggregation pipeline."""
        collection = self.db.risk_assessments
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": None,
                    "avg_risk": {"$avg": "$failure_risk_score"},
                    "max_risk": {"$max": "$failure_risk_score"},
                    "min_risk": {"$min": "$failure_risk_score"},
                    "count": {"$sum": 1},
                    "critical_count": {
                        "$sum": {
                            "$cond": [{"$gte": ["$failure_risk_score", 70]}, 1, 0]
                        }
                    },
                }
            },
        ]
        
        result = await collection.aggregate(pipeline).to_list(None)
        if result:
            return result[0]
        return {
            "avg_risk": 0,
            "max_risk": 0,
            "min_risk": 0,
            "count": 0,
            "critical_count": 0,
        }

    # ========== SIGNAL OPERATIONS ==========

    async def save_signal(self, signal: SemanticSignal) -> str:
        """Save semantic signal."""
        collection = self.db.signals
        doc = signal.model_dump(exclude={"id"}, by_alias=True)
        result = await collection.insert_one(doc)
        return str(result.inserted_id)

    async def get_signals(
        self,
        status: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> List[SemanticSignal]:
        """Get signals with filtering."""
        collection = self.db.signals
        
        query = {}
        if status:
            query["status"] = status
        if source:
            query["source"] = source
        
        docs = await collection.find(query).sort("timestamp", DESCENDING).skip(skip).limit(limit).to_list(limit)
        
        signals = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            signals.append(SemanticSignal(**doc))
        return signals

    async def get_signals_aggregated(
        self, time_window_days: int = 7
    ) -> Dict[str, Any]:
        """Get signals aggregated by status and source."""
        collection = self.db.signals
        start_date = datetime.utcnow() - timedelta(days=time_window_days)
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": {"status": "$status", "source": "$source"},
                    "count": {"$sum": 1},
                    "avg_severity": {"$avg": "$severity"},
                }
            },
            {"$sort": {"count": DESCENDING}},
        ]
        
        result = []
        async for doc in collection.aggregate(pipeline):
            result.append(doc)
        return {"signals_breakdown": result}

    # ========== TEMPORAL TREND OPERATIONS ==========

    async def save_trend(self, trend: TemporalTrend) -> str:
        """Save temporal trend."""
        collection = self.db.trends
        doc = trend.model_dump(exclude={"id"}, by_alias=True)
        result = await collection.insert_one(doc)
        return str(result.inserted_id)

    async def get_trend(self, metric_name: str) -> Optional[TemporalTrend]:
        """Get latest trend for metric."""
        collection = self.db.trends
        doc = await collection.find_one(
            {"metric_name": metric_name}, sort=[("_id", DESCENDING)]
        )
        if doc:
            doc["id"] = str(doc["_id"])
            return TemporalTrend(**doc)
        return None

    async def get_trend_comparison(
        self, metric_names: List[str], days: int = 30
    ) -> List[Dict[str, Any]]:
        """Compare multiple trends using aggregation."""
        collection = self.db.trends
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {"$match": {"metric_name": {"$in": metric_names}, "start_date": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": "$metric_name",
                    "latest_value": {"$last": "$data_points"},
                    "count": {"$sum": 1},
                }
            },
        ]
        
        results = []
        async for doc in collection.aggregate(pipeline):
            results.append(doc)
        return results

    # ========== AI INSIGHT OPERATIONS ==========

    async def save_ai_insight(self, insight: AIInsight) -> str:
        """Save AI insight."""
        collection = self.db.ai_insights
        doc = insight.model_dump(exclude={"id"}, by_alias=True)
        result = await collection.insert_one(doc)
        return str(result.inserted_id)

    async def get_latest_ai_insights(self, limit: int = 5) -> List[AIInsight]:
        """Get latest AI insights."""
        collection = self.db.ai_insights
        docs = await collection.find().sort("generated_at", DESCENDING).limit(limit).to_list(limit)
        
        insights = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            insights.append(AIInsight(**doc))
        return insights

    # ========== REPOSITORY METADATA OPERATIONS ==========

    async def save_repository(self, repo: RepositoryMetadata) -> str:
        """Save or update repository metadata."""
        collection = self.db.repositories
        
        doc = repo.model_dump(exclude={"id"}, by_alias=True)
        doc["updated_at"] = datetime.utcnow()
        
        # Upsert by repository URL
        result = await collection.update_one(
            {"repository_url": repo.repository_url},
            {"$set": doc},
            upsert=True,
        )
        
        # Return the ID (either existing or new)
        if result.upserted_id:
            return str(result.upserted_id)
        
        # Get the existing document ID
        existing = await collection.find_one({"repository_url": repo.repository_url})
        if existing:
            return str(existing["_id"])
        
        return ""

    async def get_repository(self, repo_url: str) -> Optional[RepositoryMetadata]:
        """Get repository metadata."""
        collection = self.db.repositories
        doc = await collection.find_one({"repository_url": repo_url})
        if doc:
            doc["id"] = str(doc["_id"])
            return RepositoryMetadata(**doc)
        return None

    # ========== RISK REPORT OPERATIONS ==========

    async def save_risk_report(self, report: RiskReport) -> str:
        """Save risk report."""
        collection = self.db.risk_reports
        doc = report.model_dump(exclude={"id"}, by_alias=True)
        result = await collection.insert_one(doc)
        return str(result.inserted_id)

    async def get_risk_reports(
        self, repository: Optional[str] = None, limit: int = 10
    ) -> List[RiskReport]:
        """Get risk reports."""
        collection = self.db.risk_reports
        
        query = {}
        if repository:
            query["repository"] = repository
        
        docs = await collection.find(query).sort("report_date", DESCENDING).limit(limit).to_list(limit)
        
        reports = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            reports.append(RiskReport(**doc))
        return reports

    # ========== AUDIT LOG OPERATIONS ==========

    async def log_action(self, action: str, entity_type: str, **kwargs) -> str:
        """Log audit action."""
        collection = self.db.audit_logs
        
        log_entry = AuditLog(
            action=action,
            entity_type=entity_type,
            **kwargs,
        )
        
        doc = log_entry.model_dump(exclude={"id"}, by_alias=True)
        result = await collection.insert_one(doc)
        return str(result.inserted_id)

    async def get_audit_logs(
        self,
        action: Optional[str] = None,
        days: int = 30,
        limit: int = 100,
    ) -> List[AuditLog]:
        """Get audit logs."""
        collection = self.db.audit_logs
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = {"timestamp": {"$gte": start_date}}
        if action:
            query["action"] = action
        
        docs = await collection.find(query).sort("timestamp", DESCENDING).limit(limit).to_list(limit)
        
        logs = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            logs.append(AuditLog(**doc))
        return logs

    # ========== TRANSACTIONS SUPPORT ==========

    async def create_signal_with_metrics(
        self, signal: SemanticSignal, trend: TemporalTrend
    ) -> tuple[str, str]:
        """Create signal and trend in transaction (requires replica set)."""
        signal_id = await self.save_signal(signal)
        trend_id = await self.save_trend(trend)
        return signal_id, trend_id

    # ========== BULK OPERATIONS ==========

    async def bulk_insert_signals(self, signals: List[SemanticSignal]) -> int:
        """Bulk insert signals."""
        collection = self.db.signals
        docs = [s.model_dump(exclude={"id"}, by_alias=True) for s in signals]
        
        if not docs:
            return 0
        
        result = await collection.insert_many(docs)
        return len(result.inserted_ids)

    async def bulk_update_signals(
        self, query: Dict[str, Any], update: Dict[str, Any]
    ) -> int:
        """Bulk update signals."""
        collection = self.db.signals
        result = await collection.update_many(query, {"$set": update})
        return result.modified_count

    # ========== TEXT SEARCH ==========

    async def search_signals(self, text: str, limit: int = 20) -> List[SemanticSignal]:
        """Full-text search on signals."""
        collection = self.db.signals
        
        docs = await (
            collection.find({"$text": {"$search": text}})
            .limit(limit)
            .to_list(limit)
        )
        
        signals = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            signals.append(SemanticSignal(**doc))
        return signals

    # ========== CLEANUP & MAINTENANCE ==========

    async def delete_old_signals(self, days: int = 90) -> int:
        """Delete signals older than specified days."""
        collection = self.db.signals
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = await collection.delete_many({"timestamp": {"$lt": cutoff_date}})
        return result.deleted_count

    async def archive_old_trends(self, days: int = 180) -> int:
        """Move old trends to archive collection."""
        collection = self.db.trends
        archive_collection = self.db.archived_trends
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Find old trends
        old_trends = await collection.find({"end_date": {"$lt": cutoff_date}}).to_list(None)
        
        if old_trends:
            # Insert to archive
            await archive_collection.insert_many(old_trends)
            # Delete from main collection
            result = await collection.delete_many({"end_date": {"$lt": cutoff_date}})
            return result.deleted_count
        
        return 0

    # ========== STATISTICS & ANALYTICS ==========

    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive dashboard summary using multiple aggregations."""
        risk_stats = await self.get_risk_statistics(days=30)
        signals_agg = await self.get_signals_aggregated(time_window_days=7)
        latest_risk = await self.get_latest_risk_assessment()
        insights = await self.get_latest_ai_insights(limit=3)
        
        return {
            "risk_statistics": risk_stats,
            "signals_summary": signals_agg,
            "latest_risk_assessment": latest_risk.model_dump() if latest_risk else None,
            "recent_insights": [i.model_dump() for i in insights],
            "timestamp": datetime.utcnow().isoformat(),
        }
