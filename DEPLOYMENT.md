# 🚀 Sentinel-Net v3.0: Installation & Deployment Guide

**Complete setup instructions for production deployment**

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Database Setup](#database-setup)
5. [Monitoring & Logging](#monitoring--logging)
6. [Performance Tuning](#performance-tuning)
7. [Security Hardening](#security-hardening)

---

## Local Development Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/sentinel-net.git
cd sentinel-net
```

### Step 2: Install Backend Dependencies
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt

# Download NLP data
python -c "
import nltk
nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('stopwords')
print('✅ NLTK data ready')
"

# Return to root
cd ..
```

### Step 3: Install Frontend Dependencies
```bash
# Install npm packages
npm install

# Verify installation
npm list react react-dom

# Check Node version (should be 16+)
node --version
```

### Step 4: Environment Configuration
```bash
# Copy example config
cp .env.example .env

# Edit .env (optional)
nano .env

# Key settings for development:
# VITE_API_URL=http://localhost:8000
# ENABLE_REAL_TIME_ANALYSIS=true
# ENABLE_WEBSOCKET=true
```

### Step 5: Start Development Servers
```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python -m uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
npm run dev

# Terminal 3 (optional): Monitor WebSocket
wscat -c ws://localhost:8000/ws
```

### Step 6: Verify Setup
```bash
# Test API
curl http://localhost:8000/

# Test metrics
curl http://localhost:8000/api/ml/health

# Test WebSocket (requires wscat)
wscat -c ws://localhost:8000/ws
```

---

## Production Deployment

### Pre-Deployment Checklist
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrated
- [ ] HTTPS certificates ready
- [ ] Monitoring setup
- [ ] Backup strategy in place
- [ ] Team trained on system

### Backend Deployment

#### Using Gunicorn (WSGI)
```bash
# Install production server
pip install gunicorn

# Create Procfile
cat > Procfile << EOF
web: cd backend && gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:\$PORT
EOF

# Run
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Using Daphne (ASGI - Better for WebSocket)
```bash
# Install Daphne
pip install daphne

# Daphne supports WebSocket better than Gunicorn
cd backend
daphne -b 0.0.0.0 -p 8000 main:app
```

#### Environment Variables for Production
```bash
# .env (production)
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
ENVIRONMENT=production

# Database (required for production)
DATABASE_URL=postgresql://user:password@host:5432/sentinel_net
REDIS_URL=redis://host:6379/0

# Security
CORS_ORIGINS=https://yourdomain.com
API_KEY_SECRET=your-super-secret-key-here
HTTPS_ONLY=true

# Features (can disable for performance)
ENABLE_REAL_TIME_ANALYSIS=true
ENABLE_ANOMALY_DETECTION=true
ENABLE_ML_PREDICTIONS=true

# Logging
LOG_TO_FILE=true
LOG_FILE_PATH=/var/log/sentinel-net/app.log
LOG_LEVEL=info

# Performance
ML_BATCH_SIZE=32
MAX_WORKERS=4
REQUEST_TIMEOUT=30
```

### Frontend Deployment

#### Build
```bash
# Production build
npm run build

# Output: dist/ folder with optimized files
```

#### Deploy Options

**Netlify** (Recommended for simplicity)
```bash
# Install CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=dist
```

**Vercel**
```bash
# Install CLI
npm install -g vercel

# Deploy
vercel --prod
```

**AWS S3 + CloudFront** (Enterprise)
```bash
# Build
npm run build

# Deploy to S3
aws s3 sync dist/ s3://your-bucket-name

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

#### Environment Variables for Frontend
```bash
# .env.production
VITE_API_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com
VITE_AUTO_REFRESH=true
```

---

## Docker Deployment

### Create Dockerfile (Backend)
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/')"

# Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Create Dockerfile (Frontend)
```dockerfile
# Build stage
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  # Backend
  api:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/sentinel_net
      REDIS_URL: redis://redis:6379/0
      ENVIRONMENT: production
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
    restart: unless-stopped

  # Frontend
  web:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
      - "443:443"
    environment:
      VITE_API_URL: http://api:8000
      VITE_WS_URL: ws://api:8000
    depends_on:
      - api
    restart: unless-stopped

  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: sentinel_net
    volumes:
      - db_data:/var/lib/postgresql/data
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

volumes:
  db_data:
```

### Deploy with Docker
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f web

# Stop
docker-compose down
```

---

## Database Setup

### PostgreSQL Setup (Recommended)

#### Installation
```bash
# macOS
brew install postgresql@15

# Ubuntu
sudo apt install postgresql postgresql-contrib

# Windows
# Download from https://www.postgresql.org/download/windows/
```

#### Create Database
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE sentinel_net;

# Create user
CREATE USER sentinel_user WITH PASSWORD 'your_password';

# Grant privileges
ALTER ROLE sentinel_user SET client_encoding TO 'utf8';
ALTER ROLE sentinel_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE sentinel_user SET default_transaction_deferrable TO on;
ALTER ROLE sentinel_user SET default_transaction_isolation TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE sentinel_net TO sentinel_user;
```

#### Connection String
```bash
DATABASE_URL=postgresql://sentinel_user:your_password@localhost:5432/sentinel_net
```

### Redis Setup (Caching)

#### Installation
```bash
# macOS
brew install redis

# Ubuntu
sudo apt install redis-server

# Start service
redis-server
```

#### Connection String
```bash
REDIS_URL=redis://localhost:6379/0
```

---

## Monitoring & Logging

### Backend Logging
```python
# Configure in main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/sentinel-net/app.log'),
        logging.StreamHandler()
    ]
)
```

### Frontend Error Tracking
```typescript
// Add error boundary
<ErrorBoundary>
  <App />
</ErrorBoundary>

// Log to service
import { Sentry } from '@sentry/react';

Sentry.init({
  dsn: process.env.VITE_SENTRY_DSN,
  environment: process.env.NODE_ENV
});
```

### Health Checks
```bash
# Backend health
curl http://localhost:8000/

# Database health
curl http://localhost:8000/api/ml/health

# System status dashboard
curl http://localhost:8000/api/system-data
```

### Uptime Monitoring (UptimeRobot)
```
Add endpoints:
- http://localhost:8000/  (should return 200)
- http://localhost:8000/api/metrics  (quick check)
```

---

## Performance Tuning

### Backend Optimization
```python
# Uvicorn worker count
# Rule: workers = (2 × CPU_count) + 1
# For 4 CPU: workers = 9

# In production:
uvicorn main:app --workers 9 --worker-class uvicorn.workers.UvicornWorker
```

### ML Model Caching
```python
# Cache predictions for same inputs
from functools import lru_cache

@lru_cache(maxsize=128)
def get_risk_prediction(features_hash):
    return predict_risk(features)
```

### Database Optimization
```sql
-- Create indexes for faster queries
CREATE INDEX idx_signals_timestamp ON signals(timestamp DESC);
CREATE INDEX idx_temporal_data_repo ON temporal_data(repository_id, timestamp);

-- Analyze query plans
EXPLAIN ANALYZE SELECT * FROM signals WHERE timestamp > NOW() - INTERVAL '24 hours';
```

### Frontend Performance
```js
// Code splitting
const SemanticSignalFeed = React.lazy(() => import('./components/SemanticSignalFeed'));

// Image optimization
import { Picture } from 'next/image';

// CSS minification (automatic with Vite)
npm run build
```

---

## Security Hardening

### Environment Security
```bash
# Protect .env files
chmod 600 .env
chmod 600 backend/.env

# Use strong passwords
# GitHub token: Repository scope only, no admin
# Database: Complex password, least privilege user
```

### API Security
```python
# Enable CORS properly
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS_ORIGINS", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Rate limiting
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/predict")
@limiter.limit("10/minute")
async def predict():
    pass
```

### HTTPS/SSL
```bash
# Generate self-signed certificate (development)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# Production: Use Let's Encrypt
certbot certonly --standalone -d yourdomain.com
```

---

## Disaster Recovery

### Backup Strategy
```bash
# Daily database backup
0 2 * * * pg_dump sentinel_net > /backups/sentinel_net_$(date +\%Y\%m\%d).sql

# S3 backup
aws s3 sync /backups s3://your-backup-bucket/sentinel-net/

# Retention: Keep 30 days of backups
find /backups -mtime +30 -delete
```

### Recovery Procedure
```bash
# 1. Restore specific backup
psql sentinel_net < /backups/sentinel_net_20260303.sql

# 2. Verify data integrity
psql -l  # List databases
psql sentinel_net -c "SELECT COUNT(*) FROM signals;"

# 3. Restart services
docker-compose up -d
```

---

## Scaling for Large Deployments

### Horizontal Scaling
```yaml
# Docker Compose with load balancing
services:
  api1:
    build: . backend
    # ...

  api2:
    build: ./backend
    # ...

  api3:
    build: ./backend
    # ...

  nginx:
    image: nginx:latest
    volumes:
      - ./nginx-load-balancer.conf:/etc/nginx/nginx.conf
    ports:
      - "8000:8000"
    depends_on:
      - api1
      - api2
      - api3
```

### Cache Layer
```bash
# Use Redis for analysis caching
REDIS_URL=redis://redis-cluster:6379

# Cache keys:
# analysis:{repo}:{timestamp} -> SystemData
# prediction:{features_hash} -> MLPrediction
# anomalies:{repo}:{date} -> AnomalyReport
```

### Database Sharding (Future)
```
Shard by repository:
- sentinel_net_shard1: repos A-M
- sentinel_net_shard2: repos N-Z

Or shard by time:
- sentinel_net_2026_q1
- sentinel_net_2026_q2
```

---

## Troubleshooting Deployment

### Port 8000 Already in Use
```bash
# macOS/Linux
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### WebSocket Connection Issues
```bash
# Check if API is listening on WebSocket
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  http://localhost:8000/ws

# Expected: HTTP 101 Switching Protocols
```

### Database Connection Timeout
```bash
# Verify connection string
psql postgresql://user:pass@host:5432/db

# Check network
ping host
telnet host 5432
```

### Memory Leak in ML Models
```bash
# Monitor memory usage
watch -n 1 'docker stats api'

# Restart service (recovery)
docker-compose restart api

# Add memory limits
# In docker-compose.yml:
# mem_limit: 4g
```

---

## Next Steps

1. ✅ Install locally (development)
2. ✅ Configure environment
3. ✅ Test all endpoints
4. ✅ Set up database
5. ✅ Deploy to staging
6. ✅ Run performance tests
7. ✅ Configure monitoring
8. ✅ Deploy to production

---

**Last Updated**: March 3, 2026 | **Version**: 3.0.0
