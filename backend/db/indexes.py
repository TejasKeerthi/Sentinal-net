"""MongoDB index definitions for optimal query performance."""

from pymongo import ASCENDING, DESCENDING, TEXT, GEOSPHERE
from pymongo.errors import OperationFailure
from motor.motor_asyncio import AsyncDatabase


class IndexManager:
    """Manage MongoDB indexes for collections."""

    @staticmethod
    async def create_all_indexes(db: AsyncDatabase) -> None:
        """Create all necessary indexes."""
        await IndexManager.create_risk_assessment_indexes(db)
        await IndexManager.create_signal_indexes(db)
        await IndexManager.create_trend_indexes(db)
        await IndexManager.create_ai_insight_indexes(db)
        await IndexManager.create_repository_indexes(db)
        await IndexManager.create_risk_report_indexes(db)
        await IndexManager.create_audit_log_indexes(db)

    @staticmethod
    async def create_risk_assessment_indexes(db: AsyncDatabase) -> None:
        """Risk Assessment Collection Indexes."""
        collection = db.risk_assessments
        
        # Timestamp index for sorting and range queries
        await collection.create_index(
            [("timestamp", DESCENDING)],
            name="timestamp_index",
            background=True,
        )
        
        # Risk level index for filtering
        await collection.create_index(
            [("risk_level", ASCENDING)],
            name="risk_level_index",
            background=True,
        )
        
        # Compound index for recent critical risks
        await collection.create_index(
            [("timestamp", DESCENDING), ("failure_risk_score", DESCENDING)],
            name="recent_critical_risks_index",
            background=True,
        )
        
        # TTL index for data retention (365 days)
        await collection.create_index(
            [("timestamp", ASCENDING)],
            name="ttl_365_days",
            expireAfterSeconds=31536000,
            background=True,
        )
        
        print("✓ Risk assessment indexes created")

    @staticmethod
    async def create_signal_indexes(db: AsyncDatabase) -> None:
        """Semantic Signal Collection Indexes."""
        collection = db.signals
        
        # Timestamp for sorting
        await collection.create_index(
            [("timestamp", DESCENDING)],
            name="timestamp_index",
            background=True,
        )
        
        # Status filtering
        await collection.create_index(
            [("status", ASCENDING)],
            name="status_index",
            background=True,
        )
        
        # Source filtering
        await collection.create_index(
            [("source", ASCENDING)],
            name="source_index",
            background=True,
        )
        
        # Compound index for status + timestamp (common query)
        await collection.create_index(
            [("status", ASCENDING), ("timestamp", DESCENDING)],
            name="status_timestamp_index",
            background=True,
        )
        
        # Repository filtering
        await collection.create_index(
            [("repository_url", ASCENDING)],
            name="repository_url_index",
            background=True,
        )
        
        # Commit hash for lookups
        await collection.create_index(
            [("commit_hash", ASCENDING)],
            name="commit_hash_index",
            background=True,
        )
        
        # Issue/PR number for lookups
        await collection.create_index(
            [("issue_number", ASCENDING), ("pr_number", ASCENDING)],
            name="issue_pr_index",
            background=True,
        )
        
        # Text search index on title and description
        await collection.create_index(
            [("title", TEXT), ("description", TEXT)],
            name="text_search_index",
            background=True,
        )
        
        # Tags array index
        await collection.create_index(
            [("tags", ASCENDING)],
            name="tags_index",
            background=True,
        )
        
        # TTL index (180 days)
        await collection.create_index(
            [("timestamp", ASCENDING)],
            name="ttl_180_days",
            expireAfterSeconds=15552000,
            background=True,
        )
        
        print("✓ Signal indexes created")

    @staticmethod
    async def create_trend_indexes(db: AsyncDatabase) -> None:
        """Temporal Trend Collection Indexes."""
        collection = db.trends
        
        # Metric name index
        await collection.create_index(
            [("metric_name", ASCENDING)],
            name="metric_name_index",
            background=True,
        )
        
        # Metric type index
        await collection.create_index(
            [("metric_type", ASCENDING)],
            name="metric_type_index",
            background=True,
        )
        
        # Date range index
        await collection.create_index(
            [("start_date", ASCENDING), ("end_date", ASCENDING)],
            name="date_range_index",
            background=True,
        )
        
        # Repository + metric compound index
        await collection.create_index(
            [("repository", ASCENDING), ("metric_name", ASCENDING)],
            name="repository_metric_index",
            background=True,
        )
        
        print("✓ Trend indexes created")

    @staticmethod
    async def create_ai_insight_indexes(db: AsyncDatabase) -> None:
        """AI Insight Collection Indexes."""
        collection = db.ai_insights
        
        # Timestamp for sorting
        await collection.create_index(
            [("generated_at", DESCENDING)],
            name="generated_at_index",
            background=True,
        )
        
        # Model filtering
        await collection.create_index(
            [("model_name", ASCENDING)],
            name="model_name_index",
            background=True,
        )
        
        # Affected components array search
        await collection.create_index(
            [("affected_components", ASCENDING)],
            name="affected_components_index",
            background=True,
        )
        
        print("✓ AI insight indexes created")

    @staticmethod
    async def create_repository_indexes(db: AsyncDatabase) -> None:
        """Repository Metadata Collection Indexes."""
        collection = db.repositories
        
        # Repository URL unique index (primary key)
        try:
            await collection.create_index(
                [("repository_url", ASCENDING)],
                name="repository_url_unique",
                unique=True,
                background=True,
            )
        except OperationFailure:
            pass  # Already exists
        
        # Owner index
        await collection.create_index(
            [("owner", ASCENDING)],
            name="owner_index",
            background=True,
        )
        
        # Last analyzed timestamp
        await collection.create_index(
            [("last_analyzed", DESCENDING)],
            name="last_analyzed_index",
            background=True,
        )
        
        # Enabled repositories index
        await collection.create_index(
            [("enabled", ASCENDING)],
            name="enabled_index",
            background=True,
        )
        
        print("✓ Repository indexes created")

    @staticmethod
    async def create_risk_report_indexes(db: AsyncDatabase) -> None:
        """Risk Report Collection Indexes."""
        collection = db.risk_reports
        
        # Report date index
        await collection.create_index(
            [("report_date", DESCENDING)],
            name="report_date_index",
            background=True,
        )
        
        # Repository filtering
        await collection.create_index(
            [("repository", ASCENDING)],
            name="repository_index",
            background=True,
        )
        
        # Period range index
        await collection.create_index(
            [("period_start", ASCENDING), ("period_end", ASCENDING)],
            name="period_range_index",
            background=True,
        )
        
        print("✓ Risk report indexes created")

    @staticmethod
    async def create_audit_log_indexes(db: AsyncDatabase) -> None:
        """Audit Log Collection Indexes."""
        collection = db.audit_logs
        
        # Timestamp index for range queries
        await collection.create_index(
            [("timestamp", DESCENDING)],
            name="timestamp_index",
            background=True,
        )
        
        # Action filtering
        await collection.create_index(
            [("action", ASCENDING)],
            name="action_index",
            background=True,
        )
        
        # Entity type + ID lookup
        await collection.create_index(
            [("entity_type", ASCENDING), ("entity_id", ASCENDING)],
            name="entity_lookup_index",
            background=True,
        )
        
        # User activity tracking
        await collection.create_index(
            [("user", ASCENDING), ("timestamp", DESCENDING)],
            name="user_activity_index",
            background=True,
        )
        
        # TTL index (2 years for compliance)
        await collection.create_index(
            [("timestamp", ASCENDING)],
            name="ttl_2_years",
            expireAfterSeconds=63072000,
            background=True,
        )
        
        print("✓ Audit log indexes created")

    @staticmethod
    async def rebuild_indexes(db: AsyncDatabase) -> None:
        """Rebuild all indexes (maintenance operation)."""
        collections = [
            "risk_assessments",
            "signals",
            "trends",
            "ai_insights",
            "repositories",
            "risk_reports",
            "audit_logs",
        ]
        
        for collection_name in collections:
            collection = db[collection_name]
            try:
                await collection.reindex()
                print(f"✓ Reindexed {collection_name}")
            except Exception as e:
                print(f"✗ Failed to reindex {collection_name}: {e}")

    @staticmethod
    async def get_index_stats(db: AsyncDatabase) -> dict:
        """Get statistics on collection indexes."""
        collections = [
            "risk_assessments",
            "signals",
            "trends",
            "ai_insights",
            "repositories",
            "risk_reports",
            "audit_logs",
        ]
        
        stats = {}
        for collection_name in collections:
            collection = db[collection_name]
            index_info = await collection.index_information()
            stats[collection_name] = {
                "index_count": len(index_info),
                "indexes": list(index_info.keys()),
            }
        
        return stats
