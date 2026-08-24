#!/bin/bash
# Cloudflare Pages Deployment Script for Feminism AI Dating Bot Website

echo "🌐 Deploying to Cloudflare Pages..."
echo "=================================="
echo ""

# Configuration
ACCOUNT_ID="YOUR_ACCOUNT_ID_HERE"
PROJECT_NAME="ancient-fire-1864"
API_TOKEN="cfat_YOUR_TOKEN_HERE"
SITE_DIR="cloudflare-site"

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "❌ Wrangler CLI not found. Installing..."
    npm install -g wrangler
fi

# Login to Cloudflare
echo "🔐 Logging in to Cloudflare..."
wrangler login

# Deploy to Pages
echo "📦 Deploying website to Cloudflare Pages..."
cd "$SITE_DIR"

wrangler pages deploy . \
    --project-name="$PROJECT_NAME" \
    --account-id="$ACCOUNT_ID"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo "🌐 Your website is live at:"
    echo "   https://$PROJECT_NAME.pages.dev"
    echo ""
    echo "📱 Main pages:"
    echo "   - Farsi: https://$PROJECT_NAME.pages.dev/index.html"
    echo "   - English: https://$PROJECT_NAME.pages.dev/en.html"
else
    echo ""
    echo "❌ Deployment failed. Please check your credentials and try again."
fi
