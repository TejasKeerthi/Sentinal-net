# Sentinel-Net-SE: Software Reliability Monitoring System

A professional, high-fidelity React frontend dashboard for real-time software reliability monitoring with NLP-powered semantic analysis and GitHub repository intelligence.

## 🎯 Features

- **Real-Time Risk Scoring**: Live failure risk assessment (0-100%)
- **Semantic Signal Feed**: NLP-powered analysis of commits, issues, and alerts
- **Temporal Trends Analysis**: Time-series visualization of system metrics
- **AI Insights**: Machine learning-based predictions and recommendations
- **GitHub Integration**: Analyze real GitHub repositories for reliability metrics
- **Dark Cyber Aesthetic**: Professional, modern UI with high visual fidelity

## 🏗️ Architecture

### Frontend Stack
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with custom Dark Cyber theme
- **Charts**: Recharts
- **Icons**: Lucide React

### Backend Stack
- **API**: FastAPI (Python)
- **NLP Processing**: SpaCy + TextBlob
- **GitHub Analysis**: PyGithub
- **Real-Time**: WebSocket support ready

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- Git

### Frontend Setup
```bash
npm install
npm run dev
```
Opens at `http://localhost:5173`

### Backend Setup (In separate terminal)
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python main.py
```
Backend available at `http://localhost:8000`

## 📁 Project Structure

```
sentinel-net/
├── src/
│   ├── components/              # UI components
│   │   ├── RiskScoreHero.tsx
│   │   ├── SemanticSignalFeed.tsx
│   │   ├── TemporalChart.tsx
│   │   ├── AIInsightsPanel.tsx
│   │   ├── GitHubAnalyzer.tsx
│   │   ├── Sidebar.tsx
│   │   └── RefreshButton.tsx
│   ├── pages/
│   │   ├── OverviewPage.tsx
│   │   ├── SignalsPage.tsx
│   │   ├── TrendsPage.tsx
│   │   └── ReportsPage.tsx
│   ├── hooks/
│   │   └── useSystemData.ts      # Real-time data management
│   ├── types/
│   │   └── index.ts
│   ├── data/
│   │   └── mockData.ts
│   └── App.tsx
├── backend/
│   ├── main.py                   # FastAPI server
│   ├── github_analyzer.py        # GitHub analysis
│   ├── nlp_processor.py          # NLP processing
│   └── requirements.txt
├── tailwind.config.js
├── vite.config.ts
└── package.json
```

## 🎨 Dark Cyber Color Palette

- **Deep Charcoal**: `#1a1a2e`
- **Electric Blue**: `#00d4ff`
- **Warning Orange**: `#ff6b35`
- **Cyber Gray**: `#16213e`

## 🔌 API Endpoints

### System Data
- `GET /api/system-data` - Complete system data
- `GET /api/metrics` - System metrics
- `GET /api/signals` - Recent signals
- `GET /api/temporal-data` - Trend data
- `GET /api/ai-insights` - AI predictions

### GitHub Analysis
- `GET /api/analyze-github?repo=owner/repo`
- Example: `/api/analyze-github?repo=torvalds/linux`

## 🔄 Real-Time Updates

The frontend automatically refreshes data every 30 seconds:
- Live failure risk scores
- Real-time signals with NLP analysis
- Dynamic temporal trends
- Actionable AI insights

## 📊 Dashboard Pages

### Overview
Risk score gauge, signal feed, GitHub analyzer

### Micro-Crisis Signals
Categorized signals (Urgent, Negative, Neutral)

### Temporal Trends
24-hour trends with dynamic statistics and AI insights

### Risk Reports
Current status, recommendations, export (JSON/CSV)

## 🚢 Production Build

```bash
npm run build
npm run preview
```

## ☁️ Vercel Deployment

Vercel deployment is automated through GitHub Actions via `.github/workflows/deploy-vercel.yml`.

Add these repository secrets to enable production deploys on every push to `main`:

- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`

If any secret is missing, the workflow exits as `skipped` (not failed), so CI remains stable.

## 📚 Documentation

- [Development Guide](.github/copilot-instructions.md)
- [GitHub Analysis Guide](GITHUB_ANALYSIS_GUIDE.md)
- [Python Backend Guide](PYTHON_BACKEND_GUIDE.md)
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md)

## 🔒 Security

- Input validation on API responses
- XSS protection via React
- CORS configured for development
- Environment variables for config

## 📝 License

Apache License 2.0

## 🤝 Contributing

1. Create feature branch
2. Commit changes
3. Push and open PR

---

**Status**: Production Ready ✅
**Version**: 3.0.0
**Last Updated**: February 23, 2026
