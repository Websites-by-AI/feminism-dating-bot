#!/bin/bash
# Deploy website to Cloudflare Pages using API
# Project: ancient-fire-1864

set -e

CLOUDFLARE_API_TOKEN="cfat_YOUR_TOKEN_HERE"
CLOUDFLARE_ACCOUNT_ID="YOUR_ACCOUNT_ID_HERE"
PROJECT_NAME="ancient-fire-1864"

echo "🌐 Deploying to Cloudflare Pages..."
echo "Project: $PROJECT_NAME"
echo ""

# Method 1: Try wrangler first
if command -v npx &> /dev/null; then
    echo "📦 Trying wrangler deployment..."
    cd cloudflare-site
    npx wrangler pages deploy . --project-name="$PROJECT_NAME" --account-id="$CLOUDFLARE_ACCOUNT_ID" 2>&1 || true
    cd ..
fi

# Method 2: Direct API upload
echo ""
echo "📦 Trying direct API upload..."

# Create a zip of the site
cd cloudflare-site
zip -r ../site.zip . -x "*.git*"
cd ..

# Upload via API
curl -X POST "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/pages/projects/${PROJECT_NAME}/deployments" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
  -F "file=@site.zip" \
  -H "Content-Type: multipart/form-data" || echo "Direct upload failed - use manual deployment"

echo ""
echo "🌐 Website URL: https://${PROJECT_NAME}.pages.dev"
