#!/bin/bash

# Sentinel-Net: Full-Scale ML & Real-Time Setup Guide

echo "🚀 Sentinel-Net Full-Scale Setup"
echo "=================================="
echo ""

# Step 1: Backend Setup
echo "📦 Step 1: Installing Backend Dependencies..."
cd backend

# Check Python version
python --version

# Create virtual environment
echo "Creating Python virtual environment..."
python -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # MacOS / Linux
    source venv/bin/activate
fi

# Install dependencies
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data
echo "Downloading NLTK data..."
python -c "
import nltk
nltk.download('vader_lexicon', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
print('✅ NLTK data downloaded')
"

echo "✅ Backend setup complete!"
echo ""

# Step 2: Frontend Setup
echo "📦 Step 2: Installing Frontend Dependencies..."
cd ..

npm install

echo "✅ Frontend setup complete!"
echo ""

# Step 3: Environment Configuration
echo "⚙️  Step 3: Configuring Environment..."

# Create .env file if not exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    
    # Prompt for GitHub token
    read -p "Enter your GitHub token (or press Enter to skip): " github_token
    if [ -n "$github_token" ]; then
        # Update .env file
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
            # Windows
            sed -i "s/GITHUB_TOKEN=.*/GITHUB_TOKEN=$github_token/" .env
        else
            # MacOS / Linux
            sed -i '' "s/GITHUB_TOKEN=.*/GITHUB_TOKEN=$github_token/" .env
        fi
        echo "✅ GitHub token configured"
    fi
fi

echo "✅ Environment configured!"
echo ""

# Step 4: Verify Installation
echo "🔍 Step 4: Verifying Installation..."

# Check Python packages
echo "Checking Python packages..."
python -c "import sklearn, nltk, fastapi, torch; print('✅ All Python packages installed')" 2>/dev/null || echo "⚠️  Some packages may be missing. Please check requirements.txt"

# Check npm packages
echo "Checking Node packages..."
if [ -d "node_modules" ]; then
    echo "✅ Node packages installed"
else
    echo "⚠️  Node packages not found. Run 'npm install'"
fi

echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""

echo "🎯 Next Steps:"
echo ""
echo "1. Start the Backend Server:"
echo "   cd backend"
echo "   source venv/bin/activate  # or venv\\Scripts\\activate on Windows"
echo "   python -m uvicorn main:app --reload --port 8000"
echo ""
echo "2. Start the Frontend (in another terminal):"
echo "   npm run dev"
echo ""
echo "3. Open browser:"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📚 Documentation:"
echo "   - Main Guide: README.md"
echo "   - ML & Real-Time: ML_REALTIME_GUIDE.md"
echo "   - API Reference: http://localhost:8000/docs (when running)"
echo ""
echo "🔬 Test the ML System:"
echo '   curl "http://localhost:8000/api/ml/predict-risk?commits_30d=25&contributors_30d=5"'
echo ""
echo "💻 Monitor WebSocket:"
echo "   wscat -c ws://localhost:8000/ws"
echo ""
echo "Good luck! 🚀"
