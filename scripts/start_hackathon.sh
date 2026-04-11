#!/bin/bash
set -e

# ==========================================
# Hackathon Bootstrap Script
# ==========================================
# This script handles the complete end-to-end setup for a hackathon participant.

REPO_URL="https://github.com/imraytiong/agentic-dev.git" # Replace with your actual corporate Git URL
REPO_DIR="agentic-dev"

echo "🚀 Bootstrapping Hackathon Environment..."

# 1. Clone or Pull
if [ -d "$REPO_DIR" ]; then
    echo "📂 Directory $REPO_DIR already exists. Pulling latest changes..."
    cd "$REPO_DIR"
    git pull
else
    echo "📂 Cloning repository..."
    git clone "$REPO_URL" "$REPO_DIR"
    cd "$REPO_DIR"
fi

# 2. Environment Variables
echo "⚙️  Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "   Created .env from .env.example"
fi

# 3. Python Virtual Environment
echo "🐍 Setting up Python Virtual Environment..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Gemini CLI Initialization
echo "🤖 Initializing Gemini CLI and Context..."
if command -v gemini &> /dev/null; then
    # Initialize workspace
    gemini init
    
    # Initialize Git tracking for the CLI
    gemini git init
    
    # Pin the global guardrails
    gemini context add SYSTEM_INSTRUCTIONS.md
    
    echo "   Gemini CLI initialized and System Instructions pinned!"
else
    echo "⚠️  Gemini CLI not found in PATH. Please install it before proceeding."
fi

echo ""
echo "✅ Environment Ready! You are good to go."
echo "=========================================="
echo "👉 Run the following commands to get started:"
echo "   cd $REPO_DIR"
echo "   source venv/bin/activate"
echo "   gemini load skills/adk-agent-builder/SKILL.md"
echo "=========================================="
