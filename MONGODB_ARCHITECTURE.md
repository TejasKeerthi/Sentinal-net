# MongoDB Architecture - Sentinel-Net

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│                    http://localhost:5173                     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                            │
│                http://localhost:8000                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  main.py                                             │   │
│  │  - Original ML/NLP/GitHub endpoints                  │   │
│  │  - 40+ NEW MongoDB database endpoints                │   │
│  │  - Health checks                                     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  db/ package                                         │   │
│  │  ├── config.py (Connection & pooling)               │   │
│  │  ├── models.py (8+ data models)                     │   │
│  │  ├── database.py (30+ operations)                   │   │
│  │  └── indexes.py (Index definitions)                 │   │
│  │                                                      │   │
│  │  db_migrate.py (CLI: setup, reset, migrate)         │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                   Connection Pooling (Motor)
                    Min 10, Max 50 connections
                               │
                               ▼
                    ┌──────────────────────┐
                    │   MongoDB 7.0        │
                    │  Replica Set (rs0)   │
                    │  :27017              │
                    └──────────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼
    ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
    │ Collections    │ │  Indexes       │ │   Features     │
    ├────────────────┤ ├────────────────┤ ├────────────────┤
    │ • risk_        │ │ • Compound     │ │ • Schema       │
    │   assessments  │ │ • Text Search  │ │   validation   │
    │ • signals      │ │ • TTL (auto    │ │ • Transactions │
    │ • trends       │ │   cleanup)     │ │ • Aggregation  │
    │ • ai_insights  │ │ • Unique       │ │   pipelines    │
    │ • repositories │ │   constraints  │ │ • Full-text    │
    │ • risk_reports │ └────────────────┘ │   search       │
    │ • audit_logs   │                    │ • Audit logs   │
    │ • archived_*   │                    │ • Monitoring   │
    └────────────────┘                    └────────────────┘
```

## Collection Relationships

```
┌──────────────────────────────────────────────────────────────────┐
│                    Sentinel-Net Data Model                        │
└──────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────┐
    │  Repository Metadata    │
    │  repository_url (unique)│
    │  - branch               │
    │  - enabled              │
    │  - watch_branches       │
    └────────────┬────────────┘
                 │
                 ├─────────────────────────────────────┐
                 │                                     │
                 ▼                                     ▼
    ┌────────────────────────┐          ┌──────────────────────┐
    │  Risk Assessment       │          │  Semantic Signals    │
    │  - failure_risk_score  │          │  - source (commit,   │
    │  - risk_level          │          │    issue, alert)     │
    │  - factors             │          │  - status (urgent,   │
    │  - confidence_score    │          │    negative, neutral) │
    │  - timestamp (TTL:365d)│          │  - severity          │
    └────────────┬───────────┘          │  - nlp_score         │
                 │                      │  - timestamp (TTL:180d)
                 │                      └──────┬──────────────┘
                 │                             │
                 │                    ┌────────┴──────┐
                 │                    │               │
                 │                    ▼               ▼
                 │        ┌──────────────────┐ ┌──────────────────┐
                 │        │  AI Insights     │ │   Temporal Trends│
                 │        │  - prediction    │ │  - metric_name   │
                 │        │  - confidence    │ │  - data_points   │
                 │        │  - factors       │ │  - statistics    │
                 │        │  - recommend.    │ │  - granularity   │
                 │        └──────────────────┘ └──────────────────┘
                 │
                 ▼
    ┌────────────────────────┐
    │   Risk Report          │
    │  (Aggregated view)     │
    │  - avg_risk_score      │
    │  - trend               │
    │  - signals_breakdown   │
    │  - recommendations     │
    └────────────────────────┘

    ┌────────────────────────┐
    │   Audit Log            │
    │  (Compliance trail)    │
    │  - action (CREATE,etc.)│
    │  - entity_type         │
    │  - timestamp(TTL:2yr)  │
    │  - user                │
    └────────────────────────┘
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  API Request Flow                                │
└─────────────────────────────────────────────────────────────────┘

1. Frontend Request
   ↓
2. FastAPI Endpoint (main.py)
   ├─ Validation (Pydantic)
   ├─ Dependency Injection (get_database)
   ├─ Authentication (if needed)
   └─ Authorization checks
   ↓
3. Database Layer (db/database.py)
   ├─ CRUD operations
   ├─ Aggregation pipelines
   ├─ Transaction management
   ├─ Audit logging
   └─ Error handling
   ↓
4. MongoDB
   ├─ Schema validation
   ├─ Index usage optimization
   ├─ Query execution
   └─ Connection pooling
   ↓
5. Response
   ├─ Serialize to JSON
   ├─ Add timestamps
   └─ Return to client

┌─────────────────────────────────────────────────────────────────┐
│                  Query Optimization                              │
└─────────────────────────────────────────────────────────────────┘

Fast Queries:
  GET /api/db/signals
    → Index on (status, timestamp)
    → < 50ms response

GET /api/db/signals/search
    → Text index on (title, description)
    → Full-text search < 100ms

Aggregations:
  GET /api/db/risk-assessment/statistics
    → Multi-stage pipeline
    → Computed results < 200ms

Complex Joins:
  GET /api/db/dashboard/summary
    → 4-5 parallel aggregations
    → Combined < 500ms
```

## Deployment Options

```
┌───────────────────────────────────────────────────────────────┐
│                                                               │
├──────────────────────────────────────────────────────────────┤
│  Local Development                                            │
├──────────────────────────────────────────────────────────────┤
│  MongoDB: localhost:27017                                    │
│  FastAPI: localhost:8000                                     │
│  Setup: python db_migrate.py setup                           │
│  ✓ Replica set: No (transactions disabled)                  │
│  ✓ Auth: Optional                                            │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  Docker Compose                                              │
├──────────────────────────────────────────────────────────────┤
│  Services:                                                   │
│    - MongoDB (27017) with replica set enabled              │
│    - Mongo Express (8081) admin UI                         │
│    - FastAPI (8000)                                         │
│  Setup: docker-compose up -d                               │
│  ✓ Replica set: Yes (transactions enabled)                │
│  ✓ Auth: Enabled (change credentials!)                     │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  MongoDB Atlas (Cloud)                                       │
├──────────────────────────────────────────────────────────────┤
│  Connection: mongodb+srv://user:pass@cluster.mongodb.net   │
│  Setup: Update .env, python db_migrate.py setup            │
│  ✓ Managed service (automated backups)                     │
│  ✓ Replica set: Included                                   │
│  ✓ Transactions: Yes                                        │
│  ✓ Monitoring: Built-in                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Feature Matrix

```
┌─────────────────────┬──────────┬────────┬──────────┐
│ Feature             │ Local    │ Docker │ Atlas    │
├─────────────────────┼──────────┼────────┼──────────┤
│ Standalone          │ ✅       │ ❌     │ ❌       │
│ Replica Set         │ ❌       │ ✅     │ ✅       │
│ Transactions        │ ❌       │ ✅     │ ✅       │
│ Sharding            │ ❌       │ ❌     │ ✅ (paid)│
│ Auto Backups        │ Manual   │ Manual │ ✅       │
│ Monitoring          │ Limited  │ Limited│ ✅       │
│ Authentication      │ Optional │ ✅     │ ✅       │
│ Encryption at Rest  │ ❌       │ ❌     │ ✅ (paid)│
│ IP Whitelisting     │ N/A      │ N/A    │ ✅       │
│ Connection Pooling  │ Partial  │ ✅     │ ✅       │
├─────────────────────┼──────────┼────────┼──────────┤
│ Recommended For     │ Dev/Test │ Staging│ Prod     │
└─────────────────────┴──────────┴────────┴──────────┘
```

## Index Strategy Visual

```
┌──────────────────────────────────────────────────────┐
│            Index Performance Impact                   │
└──────────────────────────────────────────────────────┘

Without Index:        With Index:
Collection Scan       Index Lookup
O(n) documents        O(log n) lookup
10,000 scans          ~14 index seeks

Example: Query signals by status
  db.signals.find({ status: "urgent" })
  
  Without (status) index:      1000ms+ (scan all docs)
  With (status) index:         ~5ms (index seek)

┌────────────────────────────────────────────────────┐
│          Created Index Types                        │
├────────────────────────────────────────────────────┤
│ Single Field Indexes                               │
│  • Field: status, source, timestamp                │
│  • Use: Fast filtering                             │
│                                                    │
│ Compound Indexes (Multi-field)                     │
│  • (status, timestamp) → Fast status+date query   │
│  • (repository, metric_name) → Fast repo lookup   │
│                                                    │
│ Text Search Index                                  │
│  • Fields: title, description                      │
│  • Use: Full-text search                           │
│                                                    │
│ TTL (Time To Live) Index                          │
│  • Auto-delete after N seconds                     │
│  • Signals: 180 days (15,552,000 sec)             │
│  • Risk: 365 days (31,536,000 sec)                │
│  • Audit: 2 years (63,072,000 sec)                │
│                                                    │
│ Unique Index                                       │
│  • repository.repository_url → Prevent duplicates │
└────────────────────────────────────────────────────┘
```

## Advanced Aggregation Example

```javascript
// Example: Get risk statistics with signal breakdown
db.risk_assessments.aggregate([
  // Stage 1: Match documents in date range
  {
    $match: {
      timestamp: { $gte: ISODate("2024-01-01") }
    }
  },
  // Stage 2: Group by risk level
  {
    $group: {
      _id: "$risk_level",
      count: { $sum: 1 },
      avg_score: { $avg: "$failure_risk_score" },
      max_score: { $max: "$failure_risk_score" }
    }
  },
  // Stage 3: Sort by count descending
  {
    $sort: { count: -1 }
  }
])

Result:
[
  {
    "_id": "high",
    "count": 245,
    "avg_score": 72.5,
    "max_score": 98
  },
  {
    "_id": "medium",
    "count": 512,
    "avg_score": 45.3,
    "max_score": 65
  },
  ...
]
```

## Performance Metrics

```
┌────────────────────────────────────────┐
│   Expected Query Performance            │
├────────────────────────────────────────┤
│ GET /latest (single doc lookup)        │ 5-10ms
│ GET /history (limit 100)               │ 20-50ms
│ GET /statistics (aggregation)          │ 50-150ms
│ GET /signals (filter + sort)           │ 10-40ms
│ POST /bulk (insert 100 docs)           │ 30-80ms
│ GET /dashboard/summary (5 agg's)       │ 100-300ms
│ GET /signals/search (text search)      │ 50-200ms
│                                        │
│ Response time target: < 500ms          │ ✅
│ Concurrent users: 50 (with pooling)    │ ✅
│ Data retention: 2+ years               │ ✅
└────────────────────────────────────────┘
```

---

**Created**: April 3, 2026
**Status**: Production Ready ✅
**MongoDB Version**: 7.0+
**Python**: 3.9+
