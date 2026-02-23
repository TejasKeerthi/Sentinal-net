# Sentinel-Net GitHub Real-Time Analysis Guide

## Overview

Sentinel-Net now analyzes **real GitHub repositories** in real-time instead of using mock data. Analyze any public repository to get:

- ✅ **Real Commits**: Latest commits and commit velocity
- ✅ **Real Issues**: Open/closed issues and bug reports  
- ✅ **Real Contributors**: Active developers and collaboration patterns
- ✅ **Risk Score**: Calculated based on actual repository metrics
- ✅ **Temporal Trends**: Commit activity over the last 7 days
- ✅ **AI Insights**: Actionable recommendations based on real data

## Setup (5 minutes)

### Step 1: Backend Running
The backend is already set up with GitHub analysis:

```bash
cd backend
.\venv\Scripts\activate
python main.py
```

Access: **http://localhost:8000**

### Step 2: Frontend Running
```bash
npm run dev
```

Access: **http://localhost:5174**

### Step 3: Open Dashboard
Go to **http://localhost:5174** and you'll see:
- GitHub Analyzer input component on the Overview page
- Enter any public GitHub repo
- Click "Analyze"

## Using the Analyzer

### Simple Examples

1. **Linux Kernel**
   ```
   owner: torvalds
   repo: linux
   Input: torvalds/linux
   ```

2. **React**
   ```
   Input: facebook/react
   ```

3. **Kubernetes**
   ```
   Input: kubernetes/kubernetes
   ```

4. **Go Programming Language**
   ```
   Input: golang/go
   ```

### Format
The analyzer accepts two formats:
- `owner/repo` (e.g., `torvalds/linux`)
- Full URL (e.g., `https://github.com/torvalds/linux`)

## What Gets Analyzed

### 1. **Real Commits** (Last 30 Days)
- Recent commit messages
- Commit timestamps
- Author information
- Commit velocity

### 2. **Real Issues**  
- Open issues count
- Issue titles and descriptions
- Bug reports
- Feature requests

### 3. **Real Contributors**
- Number of contributors
- Contribution patterns
- Collaboration metrics

### 4. **Risk Score Calculation**

```
Base Score: 50

Risk Increase:
+ 20 pts: High issue count (1 per 5 issues)
+ 25 pts: No recent commits (stale repo)
+ 15 pts: Very few commits (<5)
+ 10 pts: Many contributors (>20)

Result: Clamped between 0-100
```

Lower = Better (less risk)

### 5. **Health Status**
- 🟢 **Nominal**: Low risk (< 50)
- 🟡 **Warning**: Medium risk (50-70)  
- 🔴 **Critical**: High risk (> 85)

### 6. **Temporal Analysis**
- Commit activity per day
- Bug growth trends
- Development irregularity

### 7. **AI Insights**
- Analysis of repository health
- Contributing factors
- Actionable recommendations

## GitHub API Rate Limits

### Without Authentication (Default)
- 60 requests/hour per IP
- Works for most repositories
- _Note: Large repos might take longer_

### With Personal Token (Optional)
For higher rate limits (5,000 requests/hour):

1. **Create Token**:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token" (classic)
   - Select scopes: `public_repo`, `read:org`
   - Copy the token

2. **Set Environment Variable**:
   ```bash
   # Windows PowerShell
   $env:GITHUB_TOKEN = "your_token_here"
   python main.py
   
   # Windows CMD
   set GITHUB_TOKEN=your_token_here
   python main.py
   
   # macOS/Linux
   export GITHUB_TOKEN="your_token_here"
   python main.py
   ```

3. **Or edit `.env` file in backend:**
   ```env
   GITHUB_TOKEN=your_token_here
   ```

## API Endpoint

Direct API access (for advanced users):

```bash
# Analyze a repository
curl "http://localhost:8000/api/analyze-github?repo=torvalds/linux"

# Interactive API docs
# Swagger: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

## Example Response

```json
{
  "metrics": {
    "failureRiskScore": 45,
    "lastUpdated": "2026-02-17T14:30:00Z",
    "systemHealth": "Nominal",
    "metadata": {
      "commits_30d": 156,
      "contributors_30d": 12,
      "open_issues": 25
    }
  },
  "signals": [
    {
      "id": "abc123",
      "timestamp": "2026-02-17T14:25:00Z",
      "message": "Merge pull request #12345 from user/feature",
      "status": "Neutral",
      "source": "commit"
    }
  ],
  "temporalData": [
    {
      "timestamp": "6d ago",
      "bugGrowth": 24,
      "devIrregularity": 16
    }
  ],
  "aiInsights": {
    "title": "Repository Health Good",
    "description": "...",
    "factors": ["Regular commits", "Manageable issues"],
    "recommendation": "..."
  }
}
```

## Troubleshooting

### "Could not access repository"
- Check repo name is correct
- Some private repos require authentication
- Ensure repo is public or you have access

### Rate limit exceeded
- Common with large repos and no token
- Solution: Get a GitHub token (see above)
- Wait 1 hour for rate limit reset

### "PyGithub not installed"
```bash
# Install in backend
cd backend
.\venv\Scripts\pip install PyGithub
python main.py
```

### Slow Analysis
- Large repos (Linux, Kubernetes) take longer
- First request might cache GitHub API calls
- Try a smaller repo first

## Cool Repositories to Analyze

### Programming Languages
- `golang/go` - Go language
- `rust-lang/rust` - Rust language
- `python/cpython` - Python
- `nodejs/node` - Node.js

### Web Frameworks
- `facebook/react` - React
- `vuejs/vue` - Vue.js
- `angular/angular` - Angular
- `rails/rails` - Ruby on Rails

### DevOps & Cloud
- `kubernetes/kubernetes` - K8s
- `docker/docker` - Docker
- `hashicorp/terraform` - Terraform
- `ansible/ansible` - Ansible

### Data & AI
- `tensorflow/tensorflow` - TensorFlow
- `pytorch/pytorch` - PyTorch
- `scikit-learn/scikit-learn` - scikit-learn

## Advanced: Custom Analysis

Want to modify how analysis is calculated?

Edit: `backend/github_analyzer.py`

Key functions:
- `_calculate_risk_score()` - Risk calculation logic
- `_analyze_temporal_trends()` - Trend analysis
- `_generate_insight()` - AI insight generation
- `_extract_signals()` - Signal extraction

## Demo Script for Faculty

```
1. Open http://localhost:5174
2. Enter "torvalds/linux" in the GitHub Analyzer
3. Click "Analyze"
4. Wait for real data to load (~5 seconds)
5. Watch dashboard populate with:
   - Real commit data
   - Real issue counts
   - Risk score based on actual metrics
6. Try different repos: facebook/react, kubernetes/kubernetes
7. Show the temporal trends chart
8. Highlight the API docs at http://localhost:8000/docs
```

## Features Enabled

✅ Real GitHub API integration
✅ Real-time repository analysis  
✅ Zero configuration (works out of box)
✅ Optional GitHub token for higher limits
✅ Caching for faster repeat requests
✅ Graceful fallback to mock data
✅ Production-ready error handling

## Next Steps

1. ✅ Analyze a real repository
2. 📊 Show metrics to faculty
3. 🚀 Customize for your project
4. 🔐 Add authentication
5. 📈 Build a database to track trends over time

## Support

For issues:
1. Check PyGithub docs: https://pygithub.readthedocs.io
2. GitHub API docs: https://docs.github.com/en/rest
3. Check backend logs: `python main.py` console output

---

**Version**: 2.0.0 (GitHub Analysis Edition)
**Status**: Production Ready
**Last Updated**: February 17, 2026
