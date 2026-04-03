# MongoDB Quick Start - Get Running in 5 Minutes

## Option 1: Docker (Recommended - Easiest)

```bash
# 1. Start the entire stack
cd /path/to/sentinal-net-NLP
docker-compose up -d

# 2. Wait for services to be ready (30 seconds)
sleep 30

# 3. Verify services are running
curl http://localhost:8000/api/db/health

# 4. Access services
# - MongoDB: localhost:27017
# - Mongo Express Admin: http://localhost:8081/
# - FastAPI: http://localhost:8000/docs

# 5. Test an endpoint
curl http://localhost:8000/api/db/dashboard/summary | jq
```

### Docker Credentials
- MongoDB Admin User: `admin`
- MongoDB Admin Password: `mongodb_secure_password_change_me` (change in production!)
- Mongo Express: No auth required (running on 8081)

### Stop Services
```bash
docker-compose down          # Stop containers
docker-compose down -v       # Stop + remove volumes (DELETES DATA)
```

---

## Option 2: Local MongoDB Setup

### Prerequisites
- MongoDB 6.0+ installed locally
- Python 3.9+

### Setup Steps

```bash
# 1. Install Python dependencies
cd backend
pip install -r requirements.txt

# 2. Create environment file
cp .env.example .env

# 3. Start MongoDB (if not running)
# macOS: brew services start mongodb-community
# Linux: sudo systemctl start mongodb
# Windows: MongoDB service (installed from .msi)

# 4. Initialize database and indexes
python db_migrate.py setup

# 5. Start FastAPI server
python -m uvicorn main:app --reload

# 6. Test the API
curl http://localhost:8000/api/db/health
```

### Access Points
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- MongoDB: localhost:27017

---

## Option 3: MongoDB Atlas (Cloud)

### Setup

```bash
# 1. Create account at https://www.mongodb.com/cloud/atlas
# 2. Create a free cluster
# 3. Create database user (remember credentials)
# 4. Get connection string: mongodb+srv://user:pass@cluster.mongodb.net/

# 5. Create .env file
cd backend
cp .env.example .env

# 6. Edit .env
MONGODB_URL=mongodb+srv://your_username:your_password@your_cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=sentinel_net

# 7. Install dependencies
pip install -r requirements.txt

# 8. Initialize database
python db_migrate.py setup

# 9. Start FastAPI
python -m uvicorn main:app --reload
```

---

## Testing the API

### 1. Health Check
```bash
curl http://localhost:8000/api/db/health
```

Expected Response:
```json
{
  "status": "healthy",
  "database": "sentinel_net",
  "timestamp": "2024-04-03T12:34:56.789Z"
}
```

### 2. Get Dashboard Summary
```bash
curl http://localhost:8000/api/db/dashboard/summary | jq
```

### 3. Save Risk Assessment
```bash
curl -X POST http://localhost:8000/api/db/risk-assessment/save \
  -H "Content-Type: application/json" \
  -d '{
    "failure_risk_score": 45,
    "risk_level": "medium",
    "factors": {
      "bug_growth_rate": 0.2,
      "development_irregularity": 0.15,
      "critical_issues": 3,
      "pr_velocity": 8.5,
      "test_coverage_trend": 0.1,
      "dependency_freshness": 0.7
    },
    "confidence_score": 0.88,
    "uncertainty_score": 0.12,
    "analysis_duration_ms": 245.5
  }'
```

### 4. Get Latest Risk Assessment
```bash
curl http://localhost:8000/api/db/risk-assessment/latest | jq
```

### 5. Save a Signal
```bash
curl -X POST http://localhost:8000/api/db/signal/save \
  -H "Content-Type: application/json" \
  -d '{
    "source": "commit",
    "status": "urgent",
    "title": "Critical bug fix needed",
    "severity": 0.85,
    "nlp_score": 0.72,
    "commit_hash": "abc123def456",
    "author": "jhondoe"
  }'
```

### 6. Search Signals
```bash
curl "http://localhost:8000/api/db/signals/search?query=critical&limit=10" | jq
```

### 7. Get Audit Logs
```bash
curl "http://localhost:8000/api/db/audit-logs?days=7&limit=20" | jq
```

---

## Interactive API Testing

### Using Python
```python
import requests
import json

BASE = "http://localhost:8000/api/db"

# Health check
response = requests.get(f"{BASE}/health")
print(json.dumps(response.json(), indent=2))

# Get dashboard
response = requests.get(f"{BASE}/dashboard/summary")
print(json.dumps(response.json(), indent=2))
```

### Using Swagger UI
Open http://localhost:8000/docs in your browser
- Interactive endpoint explorer
- Try endpoints with sample data
- See real-time responses

---

## MongoDB Administration

### Access MongoDB Shell

**Docker:**
```bash
docker-compose exec mongodb mongosh
```

**Local:**
```bash
mongosh
```

**Atlas:**
```bash
mongosh "mongodb+srv://user:pass@cluster.mongodb.net/"
```

### Common Commands
```javascript
// Check database
use sentinel_net

// Show all collections
show collections

// Count documents
db.risk_assessments.countDocuments()

// View latest risk assessment
db.risk_assessments.findOne({}, { sort: { timestamp: -1 } })

// View all signals
db.signals.find()

// Check indexes
db.signals.getIndexes()

// View collection stats
db.signals.stats()
```

---

## Troubleshooting

### "Connection refused"
```bash
# Check if MongoDB is running
# Docker: docker-compose ps
# Local: mongosh (should connect)
# Atlas: Check connection string in .env
```

### "Database migrations failed"
```bash
# Check logs
docker-compose logs mongodb

# Re-run migration
python db_migrate.py reset    # WARNING: Deletes data!
python db_migrate.py setup
```

### "Indexes not created"
```bash
# Check indexes
mongosh
> use sentinel_net
> db.signals.getIndexes()
```

### "500 errors in API"
```bash
# Check FastAPI logs
docker-compose logs fastapi

# Or in local terminal:
python -m uvicorn main:app --reload --log-level debug
```

---

## File Structure Reference

```
backend/
├── db/                          # MongoDB package
│   ├── __init__.py
│   ├── config.py               # Connection config
│   ├── models.py               # Data models
│   ├── database.py             # Operations
│   └── indexes.py              # Index definitions
├── db_migrate.py               # CLI tool
├── main.py                     # FastAPI app (updated)
├── requirements.txt            # Dependencies (updated)
└── .env.example               # Config template

# Root files
docker-compose.yml             # Docker setup
mongo-init.js                  # MongoDB init script
MONGODB_SETUP.md              # Full guide
MONGODB_QUICKREF.md           # Commands
MONGODB_ARCHITECTURE.md       # Architecture
MONGODB_IMPLEMENTATION.md     # Implementation details
```

---

## Next Steps After Setup

1. **Explore the API**
   - Browse http://localhost:8000/docs
   - Try different endpoints
   - Check MongoDB for saved data

2. **Read Documentation**
   - [MONGODB_SETUP.md](MONGODB_SETUP.md) - Complete setup guide
   - [MONGODB_QUICKREF.md](MONGODB_QUICKREF.md) - Command reference
   - [MONGODB_ARCHITECTURE.md](MONGODB_ARCHITECTURE.md) - Architecture overview

3. **Test with Real Data**
   - Integrate with your GitHub analyzer
   - Save actual risk assessments
   - Create signals from commits/issues

4. **Deploy to Production**
   - Use MongoDB Atlas for hosting
   - Update .env with prod credentials
   - Configure backups and monitoring
   - Enable authentication
   - Use HTTPS for API endpoints

5. **Monitor & Maintain**
   - Check /api/db/health regularly
   - Review audit logs
   - Monitor query performance
   - Clean up old data: DELETE /api/db/cleanup

---

## API Documentation Links

### Full API Docs (when running)
http://localhost:8000/docs - Interactive Swagger UI

### Endpoint Groups

**Risk Assessments**
- `POST /api/db/risk-assessment/save` - Save assessment
- `GET /api/db/risk-assessment/latest` - Get latest
- `GET /api/db/risk-assessment/history` - Get history
- `GET /api/db/risk-assessment/statistics` - Get stats

**Signals**
- `POST /api/db/signal/save` - Save signal
- `GET /api/db/signals` - List signals
- `GET /api/db/signals/search` - Full-text search
- `POST /api/db/signals/bulk` - Bulk insert

**Trends**
- `POST /api/db/trend/save` - Save trend
- `GET /api/db/trend/{metric_name}` - Get trend
- `GET /api/db/trends/comparison` - Compare trends

**Dashboard**
- `GET /api/db/dashboard/summary` - Full summary
- `GET /api/db/health` - Health check
- `GET /api/db/audit-logs` - Audit trail

---

## Support & Help

- **Setup Issues**: Check [MONGODB_SETUP.md](MONGODB_SETUP.md) troubleshooting section
- **API Questions**: See [MONGODB_QUICKREF.md](MONGODB_QUICKREF.md)
- **Architecture**: Review [MONGODB_ARCHITECTURE.md](MONGODB_ARCHITECTURE.md)
- **Code Reference**: Check `backend/db/` package files

---

**Last Updated**: April 3, 2026
**Status**: Ready to Use ✅
