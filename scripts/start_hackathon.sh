#!/bin/bash
set -e

echo "======================================================================"
echo "🚀 Bootstrapping Hackathon Environment..."
echo "======================================================================"

echo ""
echo "🔍 Step 0: Checking Prerequisites..."

# Check Python 3
if command -v python3 &> /dev/null; then
    PY_VERSION=$(python3 --version)
    echo "✅ Python 3 found: $PY_VERSION"
else
    echo "❌ ERROR: python3 is not installed or not in PATH."
    echo "Please install Python 3 before running this script."
    exit 1
fi

# Check Gemini CLI, allowing an override via $GEMINI_CMD
GEMINI_CMD=${GEMINI_CMD:-gemini}

if ! command -v "$GEMINI_CMD" &> /dev/null; then
    echo "🔍 Checking if '$GEMINI_CMD' is an alias in your environment..."
    # Spin up an interactive subshell to load .bashrc and check `type`
    ALIAS_TARGET=$(bash -ic "type $GEMINI_CMD 2>/dev/null" | grep -i "aliased to" | awk -F"[\`']" '{print $2}')
    
    if [ -n "$ALIAS_TARGET" ]; then
        echo "✅ Detected '$GEMINI_CMD' is aliased to: $ALIAS_TARGET"
        GEMINI_CMD="$ALIAS_TARGET"
    else
        echo "⚠️  I couldn't find '$GEMINI_CMD' in your path or aliases."
        read -p "   Please enter the full path or exact command for the Gemini CLI (or press Enter to continue anyway): " user_cmd || true
        
        if [ -n "$user_cmd" ]; then
            GEMINI_CMD="$user_cmd"
            echo "   Using '$GEMINI_CMD' as the Gemini CLI command."
        else
            echo "   Continuing without explicit Gemini CLI verification..."
        fi
    fi
fi

# Verify the final command
if command -v "$GEMINI_CMD" &> /dev/null; then
    GEM_VERSION=$("$GEMINI_CMD" --version 2>/dev/null || echo "installed")
    echo "✅ Gemini CLI found ($GEMINI_CMD): $GEM_VERSION"
else
    echo "⚠️  Note: '$GEMINI_CMD' doesn't seem to be an executable path, but we will try using it."
fi

# 1. Prompt for and validate Gemini API Key
echo ""
echo "🔑 Step 1: Gemini API Key Setup"
echo "You need a valid Gemini API key to proceed."
echo "Get one at: https://aistudio.google.com/app/apikey"
VALID_KEY=""
while true; do
    read -s -p "Enter your Gemini API Key (or type 'q' to quit): " api_key || true
    echo ""
    
    if [ "$api_key" = "q" ] || [ "$api_key" = "Q" ]; then
        echo "Exiting setup."
        exit 0
    fi
    
    if [ -z "$api_key" ]; then
        echo "❌ Key cannot be empty. Please try again."
        continue
    fi

    echo "⏳ Validating key..."
    # Test the key against the models endpoint
    STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://generativelanguage.googleapis.com/v1beta/models?key=${api_key}")
    
    if [ "$STATUS_CODE" -eq 200 ]; then
        echo "✅ API Key is valid!"
        VALID_KEY="$api_key"
        
        # Export it temporarily so any gemini commands in this script work
        export GEMINI_API_KEY="$api_key"
        break
    else
        echo "❌ Invalid API Key (HTTP Status: $STATUS_CODE). Please check your key and try again."
    fi
done

# 2. Extensions (Conductor)
echo ""
echo "🔌 Step 2: Setting up extensions..."
if command -v "$GEMINI_CMD" &> /dev/null; then
    echo "⏳ Checking for Conductor extension..."
    if "$GEMINI_CMD" extension list 2>/dev/null | grep -qi "conductor"; then
        echo "✅ Conductor extension is already installed."
    else
        echo "⏳ Installing Conductor extension..."
        yes | "$GEMINI_CMD" extension install https://github.com/gemini-cli-extensions/conductor || echo "⚠️ Failed to install Conductor extension. Please install manually."
    fi
else
    echo "⚠️  Skipping extension install because '$GEMINI_CMD' is not correctly resolving."
    echo "   (Please run 'gemini extension install https://github.com/gemini-cli-extensions/conductor' manually later)."
fi

# 3. Clone or Pull Repo
REPO_URL="https://github.com/imraytiong/agentic-dev.git"
REPO_DIR="agentic-dev"

echo ""
echo "📂 Step 3: Fetching Repository..."
if [ -d "$REPO_DIR" ]; then
    echo "   Directory $REPO_DIR already exists. Pulling latest changes..."
    cd "$REPO_DIR"
    git pull origin main
else
    echo "   Cloning repository..."
    git clone "$REPO_URL" "$REPO_DIR"
    cd "$REPO_DIR"
fi

# 4. Environment Variables
echo ""
echo "⚙️  Step 4: Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "   Created .env from .env.example"
fi

# Inject the validated key into .env (works safely on Mac/Linux)
grep -v "^GEMINI_API_KEY=" .env > .env.tmp || true
echo "GEMINI_API_KEY=$VALID_KEY" >> .env.tmp
mv .env.tmp .env
echo "   Injected validated Gemini API Key into .env"

# 5. Python Virtual Environment
echo ""
echo "🐍 Step 5: Setting up Python Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   Created new virtual environment."
else
    echo "   Virtual environment already exists."
fi

# Activate and install
source venv/bin/activate
echo "   Installing dependencies (this is safe to re-run)..."
echo "   (You will see download progress bars below)"
pip install -r requirements.txt
echo "   ✅ Dependencies installed successfully."

# 6. Gemini CLI Initialization
echo ""
echo "🤖 Step 6: Initializing Gemini CLI and Context..."
if command -v "$GEMINI_CMD" &> /dev/null; then
    yes | "$GEMINI_CMD" init || true
    yes | "$GEMINI_CMD" git init || true
    yes | "$GEMINI_CMD" context add SYSTEM_INSTRUCTIONS.md || true
    yes | "$GEMINI_CMD" context add skills/adk-agent-builder/SKILL.md || true
    echo "   Gemini CLI initialized and Agent Builder skill loaded by default!"
else
    echo "⚠️  Gemini CLI not perfectly resolved in PATH. Skipping CLI initialization."
    echo "   (Once the script drops you into the shell, your command/alias will work. You can manually run your init commands)."
fi

echo ""
echo "======================================================================"
echo "✅ Environment Ready! Dropping you into the terminal..."
echo "======================================================================"

if command -v "$GEMINI_CMD" &> /dev/null; then
    exec bash --init-file <(echo "source venv/bin/activate; $GEMINI_CMD")
else
    exec bash --init-file <(echo "source venv/bin/activate")
fi