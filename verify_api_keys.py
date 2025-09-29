#!/usr/bin/env python3
"""
API Key Verification Script
Verifies that API keys are properly configured and can connect to external services.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_environment_loading():
    """Test that environment variables are loaded."""
    print("1️⃣  Testing environment configuration...")
    
    try:
        from core.config import settings
        print(f"   ✅ Settings loaded successfully")
        print(f"   📁 Export path: {settings.export_bucket_path}")
        print(f"   🗄️  Database: {settings.database_url[:50]}...")
        return settings
    except Exception as e:
        print(f"   ❌ Failed to load settings: {e}")
        return None

def test_opencorporates_key(settings):
    """Test OpenCorporates API key."""
    print("\n2️⃣  Testing OpenCorporates API key...")
    
    if not settings.opencorp_api_key:
        print("   ⚠️  OpenCorporates API key is NOT configured")
        print("   📖 Get yours at: https://opencorporates.com/api_accounts/new")
        print("   💡 Add to .env: DATAFORGE_OPENCORP_API_KEY=your_key_here")
        return False
    
    print(f"   ✅ API key is set: {settings.opencorp_api_key[:10]}...")
    
    # Test actual API call
    try:
        import httpx
        response = httpx.get(
            "https://api.opencorporates.com/v0.4/companies/search",
            params={
                "api_token": settings.opencorp_api_key,
                "q": "test",
                "jurisdiction_code": "us_ca",
                "per_page": 1
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ API key is VALID - test request successful")
            data = response.json()
            print(f"   📊 Response: {data.get('results', {}).get('companies', []).__len__()} companies returned")
            return True
        elif response.status_code == 401:
            print("   ❌ API key is INVALID - received 401 Unauthorized")
            return False
        elif response.status_code == 403:
            print("   ❌ API key is INVALID or rate limit exceeded - received 403 Forbidden")
            return False
        elif response.status_code == 429:
            print("   ⚠️  Rate limit exceeded - API key is valid but you've hit your limit")
            return True
        else:
            print(f"   ⚠️  Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to test API key: {e}")
        return False

def test_sam_api_key(settings):
    """Test SAM.gov API key."""
    print("\n3️⃣  Testing SAM.gov API key...")
    
    if not settings.sam_api_key:
        print("   ⚠️  SAM.gov API key is NOT configured")
        print("   📖 Get yours at: https://sam.gov/content/api-keys")
        print("   💡 Add to .env: DATAFORGE_SAM_API_KEY=your_key_here")
        return False
    
    print(f"   ✅ API key is set: {settings.sam_api_key[:10]}...")
    
    # Test actual API call
    try:
        import httpx
        import datetime as dt
        
        # Use recent date range
        end_date = dt.date.today()
        start_date = end_date - dt.timedelta(days=7)
        
        response = httpx.get(
            "https://api.sam.gov/opportunities/v1/search",
            headers={"X-API-KEY": settings.sam_api_key},
            params={
                "postedFrom": start_date.isoformat(),
                "postedTo": end_date.isoformat(),
                "limit": 1
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ API key is VALID - test request successful")
            data = response.json()
            total = data.get("totalRecords", 0)
            print(f"   📊 Response: {total} total opportunities available")
            return True
        elif response.status_code == 401:
            print("   ❌ API key is INVALID - received 401 Unauthorized")
            return False
        elif response.status_code == 403:
            print("   ❌ API key is INVALID - received 403 Forbidden")
            return False
        else:
            print(f"   ⚠️  Unexpected response: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to test API key: {e}")
        return False

def test_census_geocoder():
    """Test Census Geocoder (no API key needed)."""
    print("\n4️⃣  Testing Census Geocoder...")
    
    try:
        import httpx
        
        response = httpx.get(
            "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress",
            params={
                "address": "1600 Pennsylvania Ave, Washington, DC 20500",
                "benchmark": "Public_AR_Current",
                "format": "json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ Census Geocoder is accessible")
            data = response.json()
            matches = data.get("result", {}).get("addressMatches", [])
            if matches:
                county = matches[0].get("addressComponents", {}).get("county", "")
                print(f"   📍 Test geocoding successful: {county}")
            return True
        else:
            print(f"   ⚠️  Census Geocoder returned: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to test Census Geocoder: {e}")
        return False

def test_database_connection(settings):
    """Test database connection."""
    print("\n5️⃣  Testing database connection...")
    
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.fetchone()[0] == 1:
                print("   ✅ Database connection successful")
                
                # Check if tables exist
                result = conn.execute(text(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"
                ))
                table_count = result.fetchone()[0]
                print(f"   📊 Found {table_count} tables in database")
                return True
        
        return False
            
    except Exception as e:
        print(f"   ⚠️  Database connection failed: {e}")
        print("   💡 Make sure PostgreSQL is running: docker-compose up -d db")
        return False

def main():
    """Run all verification tests."""
    print("🔍 DataForge API Key Verification")
    print("=" * 50)
    print()
    
    # Test environment loading
    settings = test_environment_loading()
    if not settings:
        print("\n❌ Failed to load environment configuration")
        print("💡 Run: cp .env.sample .env and edit .env with your API keys")
        sys.exit(1)
    
    # Test API keys
    opencorp_valid = test_opencorporates_key(settings)
    sam_valid = test_sam_api_key(settings)
    census_ok = test_census_geocoder()
    db_ok = test_database_connection(settings)
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Verification Summary")
    print("=" * 50)
    
    results = {
        "OpenCorporates API": opencorp_valid,
        "SAM.gov API": sam_valid,
        "Census Geocoder": census_ok,
        "Database": db_ok
    }
    
    for name, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {name}")
    
    # Overall status
    all_valid = all(results.values())
    
    print("\n" + "=" * 50)
    if all_valid:
        print("✅ All systems operational!")
        print()
        print("Next steps:")
        print("1. Start the API: cd apps/api && uvicorn main:app --reload")
        print("2. Test the CLI: dataforge biz pull --states CA --limit 10")
        print("3. Open the UI: http://localhost:3000")
    else:
        print("⚠️  Some systems need configuration")
        print()
        if not opencorp_valid:
            print("❌ OpenCorporates: Get API key at https://opencorporates.com/api_accounts/new")
        if not sam_valid:
            print("❌ SAM.gov: Get API key at https://sam.gov/content/api-keys")
        if not db_ok:
            print("❌ Database: Run 'docker-compose up -d db'")
    
    print()
    sys.exit(0 if all_valid else 1)

if __name__ == "__main__":
    main()

