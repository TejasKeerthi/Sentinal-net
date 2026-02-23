# Sentinel-Net Python Backend Quick Start

## One-Command Setup (Windows PowerShell)

```powershell
cd backend; python -m venv venv; .\venv\Scripts\activate; pip install -r requirements.txt; python main.py
```

## One-Command Setup (macOS/Linux)

```bash
cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python main.py
```

## Step-by-Step Setup

### 1. Create & Activate Virtual Environment

**Windows:**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Backend Server

```bash
python main.py
```

Expected output:
```
INFO:     Application startup complete
Uvicorn running on http://0.0.0.0:8000
```

### 4. Test Backend

Open in browser or curl:
```
http://localhost:8000/api/system-data
```

### 5. View API Docs

```
http://localhost:8000/docs
```

## Running Frontend & Backend Together

### Terminal 1 - Backend
```powershell
cd backend
.\venv\Scripts\activate
python main.py
```

### Terminal 2 - Frontend
```powershell
npm run dev
```

### Open Dashboard
```
http://localhost:5174
```

## Project Structure

```
sentinel-net/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt         # Python dependencies
│   └── venv/                    # Virtual environment (created)
├── src/
│   ├── hooks/
│   │   └── useSystemData.ts    # Connects to backend
│   ├── components/
│   ├── pages/
│   └── ...
└── ...
```

## API Endpoints Quick Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/system-data` | Complete system data |
| GET | `/api/metrics` | Metrics only |
| GET | `/api/signals` | Recent signals |
| GET | `/api/temporal-data` | Temporal trends |
| GET | `/api/ai-insights` | AI insights |
| POST | `/api/analyze` | Trigger analysis |

## Troubleshooting

**Import Error: No module named 'fastapi'**
- Ensure virtual environment is activated
- Run: `pip install -r requirements.txt`

**Port 8000 already in use**
- Kill process: `netstat -ano | findstr :8000` then `taskkill /PID <PID> /F`
- Or use different port: `python main.py --port 8001`

**Frontend shows white screen**
- Backend may not be running
- Check: http://localhost:8000/docs
- Frontend will auto-fallback to mock data

**CORS Error in console**
- Backend CORS is configured for localhost
- For deployment, add your domain to `allow_origins` in `main.py`

## Next Steps

1. ✅ Backend running at http://localhost:8000
2. ✅ Frontend running at http://localhost:5174
3. 🔄 Modify mock data in `main.py` as needed
4. 📦 Connect to real database (PostgreSQL/MongoDB)
5. 🚀 Deploy to production (Docker/Heroku/Railway/Render)

See `PYTHON_BACKEND_GUIDE.md` for detailed documentation.
