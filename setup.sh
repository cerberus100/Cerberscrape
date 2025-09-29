#!/bin/bash
#
# DataForge Setup Script
# This script helps you set up DataForge for local development or production deployment
#

set -e  # Exit on error

echo "🔧 DataForge Setup Script"
echo "========================="
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] && [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Must be run from the dataforge directory"
    exit 1
fi

# Step 1: Check Python version
echo "1️⃣  Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "   ✅ Python ${PYTHON_VERSION} found"
    
    # Check if version is 3.9+
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 9 ]); then
        echo "   ⚠️  Warning: Python 3.9+ recommended (you have ${PYTHON_VERSION})"
    fi
else
    echo "   ❌ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

# Step 2: Install dependencies
echo ""
echo "2️⃣  Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    echo "   ✅ Dependencies installed"
else
    echo "   ❌ requirements.txt not found"
    exit 1
fi

# Step 3: Set up environment file
echo ""
echo "3️⃣  Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.sample" ]; then
        cp .env.sample .env
        echo "   ✅ Created .env file from .env.sample"
        echo "   ⚠️  IMPORTANT: Edit .env and add your API keys!"
    else
        echo "   ❌ .env.sample not found"
        exit 1
    fi
else
    echo "   ✅ .env file already exists"
fi

# Step 4: Create necessary directories
echo ""
echo "4️⃣  Creating directories..."
mkdir -p exports
mkdir -p exports/nppes_cache
mkdir -p exports/state_manual
mkdir -p exports/state_manual/mappers
mkdir -p logs
echo "   ✅ Directories created"

# Step 5: Check API keys
echo ""
echo "5️⃣  Checking API key configuration..."
source .env 2>/dev/null || true

API_KEYS_CONFIGURED=false

if [ ! -z "$DATAFORGE_OPENCORP_API_KEY" ]; then
    echo "   ✅ OpenCorporates API key is set"
    API_KEYS_CONFIGURED=true
else
    echo "   ⚠️  OpenCorporates API key is NOT set"
    echo "      Get yours at: https://opencorporates.com/api_accounts/new"
fi

if [ ! -z "$DATAFORGE_SAM_API_KEY" ]; then
    echo "   ✅ SAM.gov API key is set"
    API_KEYS_CONFIGURED=true
else
    echo "   ⚠️  SAM.gov API key is NOT set"
    echo "      Get yours at: https://sam.gov/content/api-keys"
fi

# Step 6: Test database connection
echo ""
echo "6️⃣  Testing database connection..."
if command -v psql &> /dev/null; then
    # Extract database URL from .env
    DB_URL=$(grep "^DATAFORGE_DATABASE_URL=" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    
    if echo "$DB_URL" | grep -q "localhost"; then
        echo "   ⚠️  Using local PostgreSQL database"
        echo "      Make sure PostgreSQL is running: docker-compose up -d db"
    else
        echo "   ✅ Using remote database"
    fi
else
    echo "   ℹ️  psql not found (optional for local testing)"
fi

# Step 7: Run basic tests
echo ""
echo "7️⃣  Running basic connectivity tests..."
if python3 test_basic_connectors.py 2>/dev/null; then
    echo "   ✅ Basic tests passed"
else
    echo "   ⚠️  Basic tests not run (test_basic_connectors.py not found)"
fi

# Summary
echo ""
echo "========================="
echo "✅ Setup Complete!"
echo "========================="
echo ""

if [ "$API_KEYS_CONFIGURED" = false ]; then
    echo "⚠️  NEXT STEPS REQUIRED:"
    echo ""
    echo "1. Edit the .env file and add your API keys:"
    echo "   nano .env"
    echo ""
    echo "   Required API keys:"
    echo "   - OpenCorporates: https://opencorporates.com/api_accounts/new"
    echo "   - SAM.gov: https://sam.gov/content/api-keys"
    echo ""
else
    echo "✅ API keys are configured!"
    echo ""
fi

echo "2. Start the development environment:"
echo "   docker-compose up -d"
echo ""
echo "3. Run the API:"
echo "   cd apps/api && uvicorn main:app --reload"
echo ""
echo "4. Test the CLI:"
echo "   dataforge biz pull --states CA --keywords telehealth --limit 10"
echo ""
echo "5. View the documentation:"
echo "   cat DATA_SOURCES.md"
echo "   cat API_REVIEW_AND_FIXES.md"
echo ""
echo "🎉 Happy data forging!"

