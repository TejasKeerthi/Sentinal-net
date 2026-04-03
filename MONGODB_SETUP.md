# MongoDB Advanced Integration Guide

## Overview

This guide covers the comprehensive MongoDB integration for Sentinel-Net with advanced features including schema validation, indexing, aggregation pipelines, transactions, and multiple deployment options.

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Configuration](#configuration)
3. [Database Models](#database-models)
4. [Advanced Features](#advanced-features)
5. [API Endpoints](#api-endpoints)
6. [Docker Deployment](#docker-deployment)
7. [Production Considerations](#production-considerations)
8. [Troubleshooting](#troubleshooting)

## Installation & Setup

### Prerequisites

- Python 3.9+
- MongoDB 6.0+ or MongoDB Atlas account
- Docker & Docker Compose (for containerized setup)

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure Environment

Create `.env` file from template:

```bash
cp .env.example .env
```

Edit `.env` with your MongoDB credentials:

```env
# Local Development
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=sentinel_net

# OR MongoDB Atlas
# MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
# MONGODB_DATABASE=sentinel_net_prod
```

### Step 3: Initialize Database

#### Option A: Using Docker (Recommended)

```bash
# Start MongoDB with Docker Compose
docker-compose up -d mongodb

# Create indexes and initialize
cd backend
python db_migrate.py setup
```

#### Option B: Local MongoDB Installation

```bash
# macOS
brew install mongodb-community
brew services start mongodb-community

# Linux (Ubuntu)
sudo apt-get install mongodb

# Windows
# Download from https://www.mongodb.com/try/download/community
# Run installer

# Then initialize
cd backend
python db_migrate.py setup
```

#### Option C: MongoDB Atlas (Cloud)

1. Create cluster at https://www.mongodb.com/cloud/atlas
2. Create database user with privileges
3. Get connection string: `mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority`
4. Update `.env` with connection string
5. Initialize: `python db_migrate.py setup`

## Configuration

### Environment Variables

```env
# Connection
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=sentinel_net
MONGODB_USERNAME=admin              # Optional
MONGODB_PASSWORD=password123        # Optional
MONGODB_REPLICA_SET=rs0            # Required for transactions

# Connection Pooling
MONGODB_MAX_POOL_SIZE=50
MONGODB_MIN_POOL_SIZE=10
MONGODB_SERVER_SELECTION_TIMEOUT_MS=5000
MONGODB_SOCKET_TIMEOUT_MS=30000

# Features
MONGODB_ENABLE_TRANSACTIONS=true    # Requires replica set
```

### Connection String Formats

**Local:**
```
mongodb://localhost:27017
```

**With Authentication:**
```
mongodb://user:password@localhost:27017
```

**MongoDB Atlas:**
```
mongodb+srv://user:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

**Docker Compose:**
```
mongodb://admin:mongodb_password@mongodb:27017
```

## Database Models

### Collections Overview

| Collection | Purpose | TTL | Indexes |
|-----------|---------|-----|---------|
| `risk_assessments` | System risk scores | 365 days | timestamp, risk_level |
| `signals` | Semantic signals/events | 180 days | status, source, repository_url |
| `trends` | Temporal metrics | None | metric_name, start_date |
| `ai_insights` | AI predictions | None | generated_at, model_name |
| `repositories` | Repo metadata | None | repository_url (unique) |
| `risk_reports` | Risk reports | None | report_date, repository |
| `audit_logs` | Compliance logs | 2 years | timestamp, action, user |

### Schema Validation

All collections use JSON Schema validation:

```python
# Risk Assessment
{
    "failure_risk_score": 0-100,           # Required
    "risk_level": "low|medium|high|critical",
    "factors": {
        "bug_growth_rate": 0.0-1.0,
        "development_irregularity": 0.0-1.0,
        "critical_issues": 0+,
        "pr_velocity": 0+,
        "test_coverage_trend": -1.0 to 1.0,
        "dependency_freshness": 0.0-1.0
    },
    "timestamp": datetime,                 # Required
    "confidence_score": 0.0-1.0,
    "model_name": string,
    "model_version": string
}

# Semantic Signal
{
    "source": "commit|issue|alert|metric",  # Required
    "status": "neutral|negative|urgent",    # Required
    "title": string,                        # Required
    "severity": 0.0-1.0,                   # Required
    "timestamp": datetime,                 # Required
    "nlp_score": 0.0-1.0,
    "tags": [string],
    "commit_hash": string,
    "issue_number": integer,
    "pr_number": integer
}
```

## Advanced Features

### 1. Indexing Strategy

Automatically created indexes optimize queries:

```python
# Compound indexes for common queries
- (status, timestamp): Fast signal filtering
- (repository, metric_name): Rapid metric lookups
- (timestamp, failure_risk_score): Recent critical risks

# Text search index
- (title, description): Full-text signal search

# TTL indexes for automatic cleanup
- risk_assessments: Expire after 365 days
- signals: Expire after 180 days
- audit_logs: Expire after 2 years
```

Check index statistics:

```bash
python -c "
import asyncio
from db.config import MongoDBConnection, MongoDBSettings
from db.indexes import IndexManager

async def check_indexes():
    settings = MongoDBSettings()
    MongoDBConnection.initialize(settings)
    db = await MongoDBConnection.get_async_db()
    stats = await IndexManager.get_index_stats(db)
    import json
    print(json.dumps(stats, indent=2))

asyncio.run(check_indexes())
"
```

### 2. Aggregation Pipelines

Advanced analytics using MongoDB aggregation:

```python
# Get risk statistics
pipeline = [
    {"$match": {"timestamp": {"$gte": start_date}}},
    {
        "$group": {
            "_id": None,
            "avg_risk": {"$avg": "$failure_risk_score"},
            "max_risk": {"$max": "$failure_risk_score"},
            "min_risk": {"$min": "$failure_risk_score"},
            "critical_count": {
                "$sum": {"$cond": [{"$gte": ["$failure_risk_score", 70]}, 1, 0]}
            }
        }
    }
]

# Signal distribution
pipeline = [
    {"$match": {"timestamp": {"$gte": start_date}}},
    {
        "$group": {
            "_id": {"status": "$status", "source": "$source"},
            "count": {"$sum": 1},
            "avg_severity": {"$avg": "$severity"}
        }
    }
]
```

### 3. Transactions (Advanced)

For multi-document atomic operations (requires replica set):

```python
# Example: Create signal and update trend atomically
async def create_signal_with_metrics(signal, trend):
    # Both operations succeed or both fail
    signal_id = await db.save_signal(signal)
    trend_id = await db.save_trend(trend)
    return signal_id, trend_id
```

Enable in `.env`:
```
MONGODB_REPLICA_SET=rs0
MONGODB_ENABLE_TRANSACTIONS=true
```

### 4. Connection Pooling

Optimized for production:

```env
MONGODB_MAX_POOL_SIZE=50        # Max concurrent connections
MONGODB_MIN_POOL_SIZE=10        # Min idle connections
```

Monitor connection health:

```bash
curl http://localhost:8000/api/db/health
```

### 5. Data Retention & Cleanup

Auto-delete old data:

```bash
# Delete signals older than 90 days
curl -X DELETE "http://localhost:8000/api/db/cleanup?days=90"
```

Also available: Archive old trends to separate collection.

## API Endpoints

### Health & Status

```bash
# Check MongoDB health
GET /api/db/health

# Get dashboard summary
GET /api/db/dashboard/summary
```

### Risk Assessments

```bash
# Save risk assessment
POST /api/db/risk-assessment/save
Body: SystemRiskAssessment

# Get latest assessment
GET /api/db/risk-assessment/latest

# Get history (last 30 days)
GET /api/db/risk-assessment/history?days=30&limit=100

# Get statistics
GET /api/db/risk-assessment/statistics?days=30
```

### Signals

```bash
# Save signal
POST /api/db/signal/save
Body: SemanticSignal

# Get signals with filters
GET /api/db/signals?status=urgent&source=commit&limit=50&skip=0

# Bulk insert signals
POST /api/db/signals/bulk
Body: [SemanticSignal, ...]

# Full-text search
GET /api/db/signals/search?query=critical&limit=20
```

### Trends

```bash
# Save trend
POST /api/db/trend/save
Body: TemporalTrend

# Get latest trend for metric
GET /api/db/trend/{metric_name}

# Compare trends
GET /api/db/trends/comparison?metrics=bug_growth,dev_velocity&days=30
```

### AI Insights

```bash
# Save insight
POST /api/db/ai-insight/save
Body: AIInsight

# Get latest insights
GET /api/db/ai-insights?limit=5
```

### Repositories

```bash
# Save repository metadata
POST /api/db/repository/save
Body: RepositoryMetadata

# Get repository
GET /api/db/repository/{repo_url}
```

### Risk Reports

```bash
# Save report
POST /api/db/risk-report/save
Body: RiskReport

# Get reports
GET /api/db/risk-reports?repository=myrepo&limit=10
```

### Audit Logs

```bash
# Get audit logs
GET /api/db/audit-logs?action=CREATE&days=30&limit=100
```

## Docker Deployment

### Quick Start

```bash
# Start full stack (MongoDB + Admin UI + FastAPI)
docker-compose --profile debug --profile backend up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### MongoDB Express Admin UI

Access at: http://localhost:8081

- **Username**: admin
- **Password**: mongodb_secure_password_change_me

### Service Health Checks

```bash
# MongoDB
curl mongodb:27017

# FastAPI
curl http://localhost:8000/api/db/health

# Mongo Express
curl http://localhost:8081
```

### Custom MongoDB Configuration

Edit `mongo-init.js` for replica set, users, and indexes configuration.

## Production Considerations

### 1. Security

```env
# Change default passwords
MONGODB_USERNAME=secure_username
MONGODB_PASSWORD=very_secure_password_123!

# Use MongoDB Atlas with IP whitelisting
MONGODB_URL=mongodb+srv://secure_user:secure_pass@cluster.mongodb.net/
```

### 2. Backup Strategy

```bash
# Backup MongoDB data
docker-compose exec mongodb mongodump --out /backup

# Restore from backup
docker-compose exec mongodb mongorestore /backup
```

### 3. Monitoring

Enable MongoDB profiling:

```bash
# Connect to MongoDB
mongosh

# Enable profiling
db.setProfilingLevel(1, { slowms: 100 })

# View slow queries
db.system.profile.find({ millis: { $gt: 100 } }).pretty()
```

### 4. Scaling

For high volume, consider:

- **Sharding**: Distribute data across multiple servers
- **Replica Sets**: High availability with automatic failover
- **Connection Pooling**: Increase `MONGODB_MAX_POOL_SIZE`
- **Index Strategy**: Regular index analysis and optimization

### 5. Performance Tuning

```python
# Monitor aggregation performance
pipeline = [...]
explain = await collection.aggregate(pipeline).explain()
# Check "executionStats" for query efficiency
```

## Troubleshooting

### Connection Issues

```bash
# Check if MongoDB is running
mongosh --eval "db.adminCommand('ping')"

# View connection details
curl http://localhost:8000/api/db/health

# Check port availability
netstat -an | grep 27017
```

### Index Issues

```bash
# Rebuild all indexes
python -c "
import asyncio
from db.config import MongoDBConnection, MongoDBSettings
from db.indexes import IndexManager

async def rebuild():
    MongoDBConnection.initialize(MongoDBSettings())
    db = await MongoDBConnection.get_async_db()
    await IndexManager.rebuild_indexes(db)
    await MongoDBConnection.close_async()

asyncio.run(rebuild())
"
```

### High Memory Usage

```env
# Reduce connections
MONGODB_MAX_POOL_SIZE=25
MONGODB_MIN_POOL_SIZE=5

# Enable compression
MONGODB_URL=mongodb://localhost:27017?compressors=snappy
```

### Data Validation

```bash
# Check collections
mongosh
db.risk_assessments.findOne()
db.signals.findOne()
db.validateCollection("signals")
```

## API Testing Examples

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000/api/db"

# Check health
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# Save risk assessment
assessment = {
    "failure_risk_score": 42,
    "risk_level": "medium",
    "factors": {...},
    "confidence_score": 0.92
}
response = requests.post(
    f"{BASE_URL}/risk-assessment/save",
    json=assessment
)
print(response.json())

# Get dashboard summary
response = requests.get(f"{BASE_URL}/dashboard/summary")
print(response.json())
```

### Using cURL

```bash
# Get health
curl http://localhost:8000/api/db/health

# Get dashboard
curl http://localhost:8000/api/db/dashboard/summary | jq

# Search signals
curl "http://localhost:8000/api/db/signals/search?query=critical"
```

## Next Steps

1. **Deploy to Production**: Use MongoDB Atlas for managed service
2. **Set Up Monitoring**: Use MongoDB Atlas monitoring or Datadog
3. **Implement Backup Strategy**: Scheduled MongoDB exports
4. **Performance Testing**: Load test with expected query patterns
5. **Security Audit**: Review access controls and encryption

## References

- [MongoDB Documentation](https://docs.mongodb.com/)
- [Motor Async Driver](https://motor.readthedocs.io/)
- [Pydantic Models](https://docs.pydantic.dev/)
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
