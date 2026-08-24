#!/bin/bash
# Deploy script for Feminism AI Dating Bot
# Deploys both the Telegram bot and Cloudflare Pages website

echo "🌹 Feminism AI Dating Bot - Deployment Script"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Created .env file from template${NC}"
fi

# Check bot token
TOKEN=$(grep BOT_TOKEN .env | cut -d'=' -f2)
if [ "$TOKEN" = "YOUR_BOT_TOKEN_HERE" ] || [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Bot token not set in .env${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Bot token configured${NC}"

# Check HuggingFace key
HF_KEY=$(grep HUGGINGFACE_API_KEY .env | cut -d'=' -f2)
if [ -n "$HF_KEY" ] && [ "$HF_KEY" != "hf_your_token_here" ]; then
    echo -e "${GREEN}✅ HuggingFace API key configured${NC}"
else
    echo -e "${YELLOW}⚠️  HuggingFace API key not set - AI features will use fallback mode${NC}"
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt -q
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Initialize database
echo ""
echo "🗄️ Initializing database..."
python -c "from database import init_db; init_db()"
echo -e "${GREEN}✅ Database ready${NC}"

# Start bot
echo ""
echo "🤖 Starting Telegram bot..."
echo "   Press Ctrl+C to stop"
echo ""
python main.py
