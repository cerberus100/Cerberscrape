#!/usr/bin/env python3
"""
Test script to verify all DataForge connectors are working properly.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all connectors can be imported."""
    print("Testing connector imports...")
    
    try:
        from core.pipeline.ingest.opencorporates import OpenCorporatesConnector
        print("✅ OpenCorporates connector imported successfully")
    except Exception as e:
        print(f"❌ OpenCorporates import failed: {e}")
    
    try:
        from core.pipeline.ingest.nppes import NPPESConnector
        print("✅ NPPES connector imported successfully")
    except Exception as e:
        print(f"❌ NPPES import failed: {e}")
    
    try:
        from core.pipeline.ingest.sam_opps import SAMConnector
        print("✅ SAM.gov connector imported successfully")
    except Exception as e:
        print(f"❌ SAM.gov import failed: {e}")
    
    try:
        from core.pipeline.ingest.grants_gov import GrantsGovConnector
        print("✅ Grants.gov connector imported successfully")
    except Exception as e:
        print(f"❌ Grants.gov import failed: {e}")
    
    try:
        from core.pipeline.ingest.state_manual import StateManualConnector
        print("✅ State Manual connector imported successfully")
    except Exception as e:
        print(f"❌ State Manual import failed: {e}")
    
    try:
        from core.pipeline.enrich.geocode_census import CensusGeocoder
        print("✅ Census Geocoder imported successfully")
    except Exception as e:
        print(f"❌ Census Geocoder import failed: {e}")

def test_connector_initialization():
    """Test that all connectors can be initialized."""
    print("\nTesting connector initialization...")
    
    try:
        from core.pipeline.ingest.opencorporates import OpenCorporatesConnector
        connector = OpenCorporatesConnector()
        print("✅ OpenCorporates connector initialized")
    except Exception as e:
        print(f"❌ OpenCorporates initialization failed: {e}")
    
    try:
        from core.pipeline.ingest.nppes import NPPESConnector
        connector = NPPESConnector()
        print("✅ NPPES connector initialized")
    except Exception as e:
        print(f"❌ NPPES initialization failed: {e}")
    
    try:
        from core.pipeline.ingest.sam_opps import SAMConnector
        connector = SAMConnector()
        print("✅ SAM.gov connector initialized")
    except Exception as e:
        print(f"❌ SAM.gov initialization failed: {e}")
    
    try:
        from core.pipeline.ingest.grants_gov import GrantsGovConnector
        connector = GrantsGovConnector()
        print("✅ Grants.gov connector initialized")
    except Exception as e:
        print(f"❌ Grants.gov initialization failed: {e}")
    
    try:
        from core.pipeline.ingest.state_manual import StateManualConnector
        connector = StateManualConnector()
        print("✅ State Manual connector initialized")
    except Exception as e:
        print(f"❌ State Manual initialization failed: {e}")
    
    try:
        from core.pipeline.enrich.geocode_census import CensusGeocoder
        connector = CensusGeocoder()
        print("✅ Census Geocoder initialized")
    except Exception as e:
        print(f"❌ Census Geocoder initialization failed: {e}")

def test_api_endpoints():
    """Test that API endpoints are accessible (without making actual requests)."""
    print("\nTesting API endpoint accessibility...")
    
    import httpx
    
    # Test Census Geocoder (no auth required)
    try:
        response = httpx.get(
            "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress",
            params={"address": "1600 Pennsylvania Ave, Washington, DC", "benchmark": "Public_AR_Current", "format": "json"},
            timeout=5
        )
        if response.status_code == 200:
            print("✅ Census Geocoder endpoint accessible")
        else:
            print(f"⚠️ Census Geocoder returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Census Geocoder endpoint test failed: {e}")
    
    # Test OpenCorporates (will fail without API key, but should return proper error)
    try:
        response = httpx.get(
            "https://api.opencorporates.com/v0.4/companies/search",
            params={"q": "test", "jurisdiction_code": "us_ca"},
            timeout=5
        )
        if response.status_code in [200, 401, 403]:  # 401/403 expected without API key
            print("✅ OpenCorporates endpoint accessible")
        else:
            print(f"⚠️ OpenCorporates returned status {response.status_code}")
    except Exception as e:
        print(f"❌ OpenCorporates endpoint test failed: {e}")
    
    # Test SAM.gov (will fail without API key, but should return proper error)
    try:
        response = httpx.get(
            "https://api.sam.gov/opportunities/v1/search",
            params={"postedFrom": "2024-01-01", "postedTo": "2024-01-31"},
            timeout=5
        )
        if response.status_code in [200, 401, 403]:  # 401/403 expected without API key
            print("✅ SAM.gov endpoint accessible")
        else:
            print(f"⚠️ SAM.gov returned status {response.status_code}")
    except Exception as e:
        print(f"❌ SAM.gov endpoint test failed: {e}")

def test_mock_data_generation():
    """Test that connectors can generate mock data when API keys are missing."""
    print("\nTesting mock data generation...")
    
    try:
        from core.pipeline.ingest.sam_opps import SAMConnector
        connector = SAMConnector()
        mock_data = connector._get_mock_data(
            states=["CA", "TX"],
            naics=["541511"],
            keywords=["telehealth"],
            limit=5
        )
        if mock_data and len(mock_data) > 0:
            print(f"✅ SAM.gov mock data generated: {len(mock_data)} records")
            print(f"   Sample: {mock_data[0].get('title', 'N/A')}")
        else:
            print("❌ SAM.gov mock data generation failed")
    except Exception as e:
        print(f"❌ SAM.gov mock data test failed: {e}")

def test_geocoding_functionality():
    """Test Census Geocoder functionality with a known address."""
    print("\nTesting Census Geocoder functionality...")
    
    try:
        from core.pipeline.enrich.geocode_census import CensusGeocoder
        from core.schemas import BusinessCanonical
        
        geocoder = CensusGeocoder()
        
        # Test with a known address
        test_record = BusinessCanonical(
            company_name="Test Company",
            address_line1="1600 Pennsylvania Ave",
            city="Washington",
            state="DC",
            postal_code="20500",
            country="US",
            source="test",
            last_verified=None,
            quality_score=0
        )
        
        geocoded = geocoder.geocode_record(test_record)
        
        if geocoded.county or geocoded.county_fips:
            print(f"✅ Census Geocoder working: county={geocoded.county}, fips={geocoded.county_fips}")
        else:
            print("⚠️ Census Geocoder returned no county/FIPS data")
            
    except Exception as e:
        print(f"❌ Census Geocoder test failed: {e}")

def test_state_manual_setup():
    """Test State Manual connector setup and sample mapper creation."""
    print("\nTesting State Manual connector setup...")
    
    try:
        from core.pipeline.ingest.state_manual import StateManualConnector, create_sample_mapper
        
        # Test sample mapper creation
        mapper_path = create_sample_mapper("CA")
        if mapper_path.exists():
            print(f"✅ Sample mapper created: {mapper_path}")
        else:
            print("❌ Sample mapper creation failed")
        
        # Test connector initialization
        connector = StateManualConnector()
        if connector.data_dir.exists():
            print(f"✅ State Manual data directory created: {connector.data_dir}")
        else:
            print("❌ State Manual data directory creation failed")
            
    except Exception as e:
        print(f"❌ State Manual setup test failed: {e}")

def test_pipeline_integration():
    """Test that the updated pipelines can import and use the new connectors."""
    print("\nTesting pipeline integration...")
    
    try:
        from core.pipeline.business import run_business_pipeline
        from core.pipeline.rfp import run_rfp_pipeline
        from core.schemas import BusinessPullRequest, RFPPullRequest
        
        print("✅ Business pipeline imported successfully")
        print("✅ RFP pipeline imported successfully")
        
        # Test schema creation
        biz_request = BusinessPullRequest(
            states=["CA"],
            keywords=["test"],
            limit=10
        )
        print("✅ BusinessPullRequest schema working")
        
        rfp_request = RFPPullRequest(
            states=["CA"],
            keywords=["test"],
            limit=10
        )
        print("✅ RFPPullRequest schema working")
        
    except Exception as e:
        print(f"❌ Pipeline integration test failed: {e}")

def main():
    """Run all connector tests."""
    print("🔧 DataForge Connector Test Suite")
    print("=" * 50)
    
    test_imports()
    test_connector_initialization()
    test_api_endpoints()
    test_mock_data_generation()
    test_geocoding_functionality()
    test_state_manual_setup()
    test_pipeline_integration()
    
    print("\n" + "=" * 50)
    print("✅ Connector test suite completed!")
    print("\nNext steps:")
    print("1. Set API keys in .env file for full functionality")
    print("2. Run 'make up' to start the development environment")
    print("3. Test the API endpoints with real data")

if __name__ == "__main__":
    main()

