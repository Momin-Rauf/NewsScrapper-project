#!/bin/bash

# Render CLI Deployment Script
# This script deploys your NewsScrapper project directly to Render

echo "🚀 Deploying NewsScrapper to Render..."

# Check if render CLI is installed
if ! command -v render &> /dev/null; then
    echo "❌ Render CLI not found. Installing..."
    curl -s https://api.render.com/downloads/cli/install.sh | bash
    export PATH="$HOME/.render/bin:$PATH"
fi

# Login to Render (if not already logged in)
echo "🔐 Logging into Render..."
render login

# Deploy Web Service
echo "🌐 Deploying Web Service..."
render blueprint apply render.yaml

echo "✅ Deployment complete!"
echo "📱 Your app will be available at: https://your-app-name.onrender.com"
echo "🔧 Check the Render dashboard for deployment status and logs" 