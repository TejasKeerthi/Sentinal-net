# Sentinel-Net Python Backend Setup Guide

## Overview

Sentinel-Net uses a Python FastAPI backend to provide REST API endpoints for the React frontend dashboard. This guide covers installation, configuration, and running the backend.

## Stack

- **Framework**: FastAPI
- **Server**: Uvicorn
- **Data Validation**: Pydantic
- **Python**: 3.8+

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended: venv or conda)

## Installation

### 1. Create Python Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **pydantic**: Data validation
- **python-multipart**: Form data support

## Running the Backend

### Development Mode (with auto-reload)

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at: **http://localhost:8000**

### Production Mode (without auto-reload)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Health Check
```
GET /
```
Returns service status and version

### Get Complete System Data
```
GET /api/system-data
```
Returns all metrics, signals, temporal data, and AI insights

**Response:**
```json
{
  "metrics": {
    "failureRiskScore": 72,
    "lastUpdated": "2026-02-17T14:30:00Z",
    "systemHealth": "Warning"
  },
  "signals": [...],
  "temporalData": [...],
  "aiInsights": {...}
}
```

### Get Metrics Only
```
GET /api/metrics
```

### Get Signals
```
GET /api/signals?limit=20
```

### Get Temporal Data
```
GET /api/temporal-data
```

### Get AI Insights
```
GET /api/ai-insights
```

### Trigger Analysis
```
POST /api/analyze
```

## Frontend Integration

The React frontend is configured to connect to the FastAPI backend automatically:

1. **Component**: `src/hooks/useSystemData.ts`
2. **Backend URL**: `http://localhost:8000`
3. **Fallback**: Uses mock data if backend is unavailable

### Automatic Fallback

If the backend is not running:
- Frontend will use mock data automatically
- No errors in console
- Dashboard remains fully functional

### Connecting Backend & Frontend

**Terminal 1** - Start Python Backend:
```bash
cd backend
python main.py
```

**Terminal 2** - Start React Frontend:
```bash
cd sentinel-net (root)
npm run dev
```

Open browser: **http://localhost:5174** (or 5173)

## Development Workflow

### Adding New Endpoints

1. **Define Pydantic Model** in `main.py`:
```python
class NewDataModel(BaseModel):
    field1: str
    field2: int
```

2. **Create Endpoint**:
```python
@app.get("/api/new-endpoint", response_model=NewDataModel)
async def get_new_data():
    return NewDataModel(field1="value", field2=42)
```

3. **Test in Browser**:
```
http://localhost:8000/api/new-endpoint
```

### Database Integration (Future)

To add a database (PostgreSQL, MongoDB, etc.):

1. Install database adapter:
   ```bash
   pip install sqlalchemy psycopg2-binary  # For PostgreSQL
   ```

2. Create database models:
   ```python
   from sqlalchemy import Column, Integer, String
   from sqlalchemy.ext.declarative import declarative_base
   
   Base = declarative_base()
   
   class Signal(Base):
       __tablename__ = "signals"
       id = Column(Integer, primary_key=True)
       message = Column(String)
   ```

3. Replace mock data functions with database queries

## Deployment

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t sentinel-net-backend .
docker run -p 8000:8000 sentinel-net-backend
```

### Cloud Deployment (Heroku, Railway, Render)

1. Set environment variable for port:
   ```
   PORT=8000
   ```

2. Update main startup to use environment port:
   ```python
   import os
   port = int(os.getenv("PORT", 8000))
   uvicorn.run(app, host="0.0.0.0", port=port)
   ```

3. Deploy using platform-specific instructions

## Troubleshooting

### Port Already in Use

If port 8000 is already used:

```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (Windows)
taskkill /PID <PID> /F

# Or use different port
uvicorn main:app --reload --port 8001
```

### CORS Errors

CORS is already configured for:
- `http://localhost:5173`
- `http://localhost:5174`
- `http://localhost:3000`

To add more origins, modify:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://your-domain.com"],
    ...
)
```

### Virtual Environment Issues

Ensure you're in the virtual environment:

```bash
# Check Python path (should show venv path)
where python

# On macOS/Linux:
which python
```

## Performance Tips

1. **Use production mode** for deployment (no auto-reload)
2. **Enable GZIP compression**:
   ```python
   from fastapi.middleware.gzip import GZIPMiddleware
   app.add_middleware(GZIPMiddleware, minimum_size=1000)
   ```

3. **Use connection pooling** for databases
4. **Cache data** with Redis for frequently accessed endpoints
5. **Use async/await** for all I/O operations

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Both are live and allow testing endpoints directly.

## Environment Variables

Create `.env` file for configuration:

```env
DATABASE_URL=postgresql://user:password@localhost/sentinel
ENVIRONMENT=development
DEBUG=True
```

Load with python-dotenv:
```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
import os

load_dotenv()
database_url = os.getenv("DATABASE_URL")
```

## Monitoring & Logging

Add logging for production:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/api/system-data")
async def get_system_data():
    logger.info("System data requested")
    return await get_system_data()
```

## Testing

Create `test_main.py`:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/")
    assert response.status_code == 200

def test_system_data():
    response = client.get("/api/system-data")
    assert response.status_code == 200
    assert "metrics" in response.json()

if __name__ == "__main__":
    test_health()
    test_system_data()
    print("All tests passed!")
```

Run tests:
```bash
python test_main.py
```

## Next Steps

1. Start the backend: `python main.py`
2. Start the frontend: `npm run dev`
3. Open dashboard: http://localhost:5174
4. Modify mock data in `main.py` as needed
5. Connect to real database when ready

## Support

For issues:
1. Check FastAPI docs: https://fastapi.tiangolo.com
2. Check Pydantic docs: https://docs.pydantic.dev
3. Review CORS configuration if frontend can't connect
4. Use `/docs` endpoint to test API manually

---

**Last Updated**: February 17, 2026
**Version**: 1.0.0
