#!/usr/bin/env python3
"""
Test Real Data Pulling Script
This script demonstrates what happens when you try to pull real data from the APIs.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_without_api_keys():
    """Test what happens without API keys (mock data)."""
    print("🔍 Testing WITHOUT API Keys (Mock Data)")
    print("=" * 50)
    
    try:
        from core.pipeline.ingest.opencorporates import opencorp_connector
        from core.pipeline.ingest.sam_opps import sam_connector
        
        # Test OpenCorporates without API key
        print("\n1️⃣  OpenCorporates (No API Key)")
        opencorp_results = opencorp_connector.search_companies(
            states=["CA"],
            naics=["621111"],
            keywords=["telehealth"],
            limit=5
        )
        print(f"   Results: {len(opencorp_results)} companies")
        if opencorp_results:
            print(f"   Sample: {opencorp_results[0].get('company_name', 'N/A')}")
        else:
            print("   ⚠️  No results (API key required)")
        
        # Test SAM.gov without API key
        print("\n2️⃣  SAM.gov (No API Key)")
        sam_results = sam_connector.search_opportunities(
            states=["CA"],
            naics=["541511"],
            keywords=["telehealth"],
            limit=5
        )
        print(f"   Results: {len(sam_results)} opportunities")
        if sam_results:
            print(f"   Sample: {sam_results[0].get('title', 'N/A')}")
        else:
            print("   ⚠️  No results (API key required)")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_with_api_keys():
    """Test what happens with API keys (real data)."""
    print("\n🔑 Testing WITH API Keys (Real Data)")
    print("=" * 50)
    
    try:
        from core.config import settings
        
        # Check if API keys are configured
        opencorp_key = settings.opencorp_api_key
        sam_key = settings.sam_api_key
        
        print(f"\n1️⃣  API Key Status")
        print(f"   OpenCorporates: {'✅ SET' if opencorp_key else '❌ NOT SET'}")
        print(f"   SAM.gov: {'✅ SET' if sam_key else '❌ NOT SET'}")
        
        if not opencorp_key and not sam_key:
            print("\n   ⚠️  No API keys configured - will use mock data")
            print("   💡 To get real data:")
            print("      - OpenCorporates: https://opencorporates.com/api_accounts/new")
            print("      - SAM.gov: https://sam.gov/content/api-keys")
            return
        
        # Test with actual API calls
        if opencorp_key:
            print(f"\n2️⃣  OpenCorporates Real Data Test")
            try:
                from core.pipeline.ingest.opencorporates import opencorp_connector
                
                results = opencorp_connector.search_companies(
                    states=["CA"],
                    naics=["621111"],
                    keywords=["telehealth"],
                    limit=3
                )
                print(f"   ✅ Real data: {len(results)} companies found")
                for i, company in enumerate(results[:2]):
                    print(f"   {i+1}. {company.get('company_name', 'N/A')} - {company.get('city', 'N/A')}, {company.get('state', 'N/A')}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        if sam_key:
            print(f"\n3️⃣  SAM.gov Real Data Test")
            try:
                from core.pipeline.ingest.sam_opps import sam_connector
                import datetime as dt
                
                # Use recent date range
                end_date = dt.date.today()
                start_date = end_date - dt.timedelta(days=7)
                
                results = sam_connector.search_opportunities(
                    states=["CA"],
                    naics=["541511"],
                    keywords=["telehealth"],
                    posted_from=start_date.isoformat(),
                    posted_to=end_date.isoformat(),
                    limit=3
                )
                print(f"   ✅ Real data: {len(results)} opportunities found")
                for i, opp in enumerate(results[:2]):
                    print(f"   {i+1}. {opp.get('title', 'N/A')} - {opp.get('agency', 'N/A')}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_census_geocoder():
    """Test Census Geocoder (no API key needed)."""
    print("\n🌍 Testing Census Geocoder (No API Key Required)")
    print("=" * 50)
    
    try:
        from core.pipeline.enrich.geocode_census import census_geocoder
        from core.schemas import BusinessCanonical
        
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
        
        print("\n1️⃣  Geocoding Test Address")
        print(f"   Input: {test_record.address_line1}, {test_record.city}, {test_record.state} {test_record.postal_code}")
        
        geocoded = census_geocoder.geocode_record(test_record)
        
        if geocoded.county or geocoded.county_fips:
            print(f"   ✅ Success: County={geocoded.county}, FIPS={geocoded.county_fips}")
        else:
            print("   ⚠️  No county/FIPS data returned")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_full_pipeline():
    """Test the full pipeline with mock data."""
    print("\n🔄 Testing Full Pipeline (Mock Data)")
    print("=" * 50)
    
    try:
        from core.pipeline.business import run_business_pipeline
        from core.pipeline.rfp import run_rfp_pipeline
        from core.schemas import BusinessPullRequest, RFPPullRequest
        import datetime as dt
        
        # Test business pipeline
        print("\n1️⃣  Business Pipeline Test")
        biz_payload = BusinessPullRequest(
            states=["CA"],
            keywords=["telehealth"],
            limit=5,
            enable_geocoder=True
        )
        
        print(f"   Request: {biz_payload.states} states, keywords: {biz_payload.keywords}, limit: {biz_payload.limit}")
        
        biz_result = run_business_pipeline(biz_payload)
        print(f"   ✅ Result: {biz_result.message}")
        print(f"   📊 Export path: {biz_result.export_path}")
        print(f"   🎯 QA Report: {'PASS' if biz_result.qa_report.passed else 'FAIL'}")
        
        # Test RFP pipeline
        print("\n2️⃣  RFP Pipeline Test")
        rfp_payload = RFPPullRequest(
            states=["CA"],
            keywords=["telehealth"],
            limit=5
        )
        
        print(f"   Request: {rfp_payload.states} states, keywords: {rfp_payload.keywords}, limit: {rfp_payload.limit}")
        
        rfp_result = run_rfp_pipeline(rfp_payload)
        print(f"   ✅ Result: {rfp_result.message}")
        print(f"   📊 Export path: {rfp_result.export_path}")
        print(f"   🎯 QA Report: {'PASS' if rfp_result.qa_report.passed else 'FAIL'}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    """Run all tests."""
    print("🧪 DataForge Real Data Pulling Test")
    print("=" * 60)
    print()
    
    # Test without API keys (mock data)
    test_without_api_keys()
    
    # Test with API keys (real data)
    test_with_api_keys()
    
    # Test Census Geocoder (no key needed)
    test_census_geocoder()
    
    # Test full pipeline
    test_full_pipeline()
    
    print("\n" + "=" * 60)
    print("📋 Summary")
    print("=" * 60)
    print()
    print("✅ What works without API keys:")
    print("   - Census Geocoder (address verification)")
    print("   - NPPES (healthcare bulk files)")
    print("   - State Manual (CSV drop)")
    print("   - Mock data for testing")
    print()
    print("⚠️  What requires API keys:")
    print("   - OpenCorporates (business data)")
    print("   - SAM.gov (RFP data)")
    print("   - Grants.gov (grant data)")
    print()
    print("🔑 To get real data:")
    print("   1. Get OpenCorporates key: https://opencorporates.com/api_accounts/new")
    print("   2. Get SAM.gov key: https://sam.gov/content/api-keys")
    print("   3. Add to .env file")
    print("   4. Run: python3 verify_api_keys.py")
    print()
    print("🚀 Then you can pull real data:")
    print("   dataforge biz pull --states CA --limit 100")
    print("   dataforge rfp pull --states CA --limit 100")

if __name__ == "__main__":
    main()
