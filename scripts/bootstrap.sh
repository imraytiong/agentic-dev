#!/bin/bash

echo "🚀 Bootstrapping Hackathon Environment..."

# 1. Python Environment Setup
echo "🐍 Setting up Python Virtual Environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "   Created .env from .env.example"
fi

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Gemini CLI Initialization
echo "🤖 Initializing Gemini CLI and Context..."
if command -v gemini &> /dev/null; then
    gemini init
    gemini git init
    gemini context add SYSTEM_INSTRUCTIONS.md
    echo "   Gemini CLI initialized and System Instructions pinned!"
else
    echo "⚠️  Gemini CLI not found in PATH. Please ensure it is installed (npm install -g @google/generative-ai-cli)."
fi

echo ""
echo "✅ Environment Ready!"
echo "👉 Run 'source venv/bin/activate' to activate your Python environment."
echo "👉 You can now load your skills and start building!"
