#!/usr/bin/env python3
"""Quick test script to validate the Aetheria API setup."""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath('.'))

def test_imports():
    """Test that all main modules can be imported."""
    print("🧪 Testing module imports...")
    
    try:
        from app.core.config import get_settings
        print("✅ app.core.config imported successfully")
        
        settings = get_settings()
        print(f"✅ Settings loaded: env={settings.app_env}, tz={settings.timezone}")
        
    except Exception as e:
        print(f"❌ Failed to import config: {e}")
        return False
    
    try:
        from app.core.logging import get_logger, configure_logging
        configure_logging()
        logger = get_logger("test")
        logger.info("Test log message")
        print("✅ app.core.logging imported and configured successfully")
        
    except Exception as e:
        print(f"❌ Failed to import logging: {e}")
        return False
    
    try:
        from app.schemas.common import BaseResponse, HealthResponse
        response = BaseResponse(success=True, message="Test")
        print("✅ app.schemas.common imported successfully")
        
    except Exception as e:
        print(f"❌ Failed to import schemas: {e}")
        return False
    
    try:
        from app.services.rules_engine import evaluate_treatment_rules
        print("✅ app.services.rules_engine imported successfully")
        
    except Exception as e:
        print(f"❌ Failed to import services: {e}")
        return False
    
    return True

def test_fastapi_app():
    """Test FastAPI app creation."""
    print("\n🚀 Testing FastAPI app creation...")
    
    try:
        from app.main import app
        print("✅ FastAPI app created successfully")
        print(f"✅ App title: {app.title}")
        print(f"✅ App version: {app.version}")
        
        # Check routes
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/healthz"]
        
        for route in expected_routes:
            if route in routes:
                print(f"✅ Route {route} found")
            else:
                print(f"⚠️  Route {route} not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create FastAPI app: {e}")
        return False

def main():
    """Main test function."""
    print("🔍 Aetheria API - Setup Validation")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test FastAPI app
    app_ok = test_fastapi_app()
    
    print("\n" + "=" * 50)
    if imports_ok and app_ok:
        print("🎉 All tests passed! The Aetheria API is ready to run.")
        print("\n💡 Next steps:")
        print("1. Install dependencies: pip install -e .[dev]")
        print("2. Run the server: uvicorn app.main:app --reload")
        print("3. Test: curl http://localhost:8000/healthz")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
