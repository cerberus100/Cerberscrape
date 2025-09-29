#!/usr/bin/env python3
"""Basic test script to verify DataForge core functionality without external dependencies."""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that core modules can be imported."""
    print("🧪 Testing core module imports...")
    
    try:
        import core.schemas
        print("✅ core.schemas imported successfully")
    except Exception as e:
        print(f"❌ core.schemas import failed: {e}")
        return False
    
    try:
        import core.config
        print("✅ core.config imported successfully")
    except Exception as e:
        print(f"❌ core.config import failed: {e}")
        return False
    
    try:
        import core.aws
        print("✅ core.aws imported successfully")
    except Exception as e:
        print(f"❌ core.aws import failed: {e}")
        return False
    
    return True

def test_schemas():
    """Test Pydantic schema validation."""
    print("\n🧪 Testing schema validation...")
    
    try:
        from core.schemas import BusinessPullRequest, RFPPullRequest, HealthResponse
        import datetime as dt
        
        # Test BusinessPullRequest
        biz_req = BusinessPullRequest(
            states=["CA", "TX"],
            naics=["621111"],
            limit=100
        )
        print("✅ BusinessPullRequest validation passed")
        
        # Test RFPPullRequest
        rfp_req = RFPPullRequest(
            states=["NY"],
            keywords=["telehealth"],
            limit=50
        )
        print("✅ RFPPullRequest validation passed")
        
        # Test HealthResponse
        health = HealthResponse(ok=True, ts=dt.datetime.utcnow())
        print("✅ HealthResponse validation passed")
        
        return True
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False

def test_config():
    """Test configuration loading."""
    print("\n🧪 Testing configuration...")
    
    try:
        from core.config import settings
        
        print(f"✅ Database URL: {settings.database_url[:50]}...")
        print(f"✅ Export path: {settings.export_bucket_path}")
        print(f"✅ Environment: {settings.environment}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_aws_utilities():
    """Test AWS utility classes."""
    print("\n🧪 Testing AWS utilities...")
    
    try:
        from core.aws import S3Exporter, RDSManager, SecretsManager
        
        # Test S3Exporter initialization
        s3_exporter = S3Exporter()
        print("✅ S3Exporter initialized")
        
        # Test RDSManager
        rds_url = RDSManager.get_connection_string()
        print(f"✅ RDS connection string: {rds_url[:50]}...")
        
        # Test SecretsManager
        secrets = SecretsManager()
        print("✅ SecretsManager initialized")
        
        return True
    except Exception as e:
        print(f"❌ AWS utilities test failed: {e}")
        return False

def main():
    """Run all basic tests."""
    print("🚀 DataForge Basic Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_schemas,
        test_config,
        test_aws_utilities,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print("❌ Test failed, stopping...")
            break
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed! DataForge is ready for deployment.")
        return 0
    else:
        print("💥 Some tests failed. Please fix issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

