#!/bin/bash

# School AI API Startup Script

echo "🚀 Starting School AI API..."
echo "================================"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    echo "Run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create .env file with your OpenAI API key."
    echo "Example: OPENAI_API_KEY=your_api_key_here"
    exit 1
fi

# Activate virtual environment and start the server
echo "📦 Activating virtual environment..."
source .venv/bin/activate

echo "🔑 Loading environment variables..."
export $(cat .env | xargs)

echo "🌐 Starting FastAPI server..."
echo "📍 API will be available at: http://localhost:8000"
echo "📚 Documentation at: http://localhost:8000/docs"
echo "🔄 Press Ctrl+C to stop the server"
echo ""

python main.py