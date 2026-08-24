#!/bin/bash
# Quick start script for AI Dating Bot

echo "🌹 AI Dating Telegram Bot - Setup"
echo "=================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
fi

# Check if bot token is set
TOKEN=$(grep BOT_TOKEN .env | cut -d'=' -f2)
if [ "$TOKEN" = "YOUR_BOT_TOKEN_HERE" ] || [ -z "$TOKEN" ]; then
    echo ""
    echo "⚠️  Bot token not set!"
    echo ""
    echo "To get your bot token:"
    echo "1. Open Telegram and message @BotFather"
    echo "2. Send /newbot and follow the instructions"
    echo "3. Copy the token and paste it in .env file"
    echo ""
    echo "Edit .env and set: BOT_TOKEN=your_token_here"
    exit 1
fi

# Check if Python dependencies are installed
if ! python3 -c "import telegram" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "🚀 Starting bot..."
echo "   Press Ctrl+C to stop"
echo ""
python3 main.py
