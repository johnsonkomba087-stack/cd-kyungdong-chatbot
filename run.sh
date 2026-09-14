#!/bin/bash
set -e

echo "🎓 Kyungdong University RAG Chatbot"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "🚀 Starting Streamlit app..."
echo "📍 Open your browser to: http://localhost:8501"
echo ""
echo "⏹️  Press Ctrl+C to stop"
echo ""

# Run Streamlit
streamlit run app.py