"""
Test script to verify CORS configuration is working correctly.
This script makes a request to the backend API and checks if CORS headers are present.
"""
import requests

def test_cors():
    """Test CORS configuration by making requests to the backend."""
    backend_url = "http://localhost:8000"
    frontend_origin = "http://localhost:5173"
    
    print("=" * 60)
    print("Testing CORS Configuration")
    print("=" * 60)
    print(f"\nBackend URL: {backend_url}")
    print(f"Frontend Origin: {frontend_origin}")
    
    # Test 1: Simple GET request (health check)
    print("\n1. Testing simple GET request to /health")
    try:
        response = requests.get(
            f"{backend_url}/health",
            headers={"Origin": frontend_origin}
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'NOT PRESENT')}")
        print(f"   Access-Control-Allow-Credentials: {response.headers.get('Access-Control-Allow-Credentials', 'NOT PRESENT')}")
        
        if response.headers.get('Access-Control-Allow-Origin'):
            print("   ✅ CORS headers present")
        else:
            print("   ❌ CORS headers missing")
    except requests.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 2: OPTIONS preflight request
    print("\n2. Testing OPTIONS preflight request to /api/v1/ai/balance-suggestions")
    try:
        response = requests.options(
            f"{backend_url}/api/v1/ai/balance-suggestions",
            headers={
                "Origin": frontend_origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "content-type"
            }
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'NOT PRESENT')}")
        print(f"   Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'NOT PRESENT')}")
        print(f"   Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', 'NOT PRESENT')}")
        
        if response.headers.get('Access-Control-Allow-Origin'):
            print("   ✅ Preflight CORS headers present")
        else:
            print("   ❌ Preflight CORS headers missing")
    except requests.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 3: Check backend configuration
    print("\n3. Checking backend configuration")
    try:
        from app.core.config import settings
        print(f"   Configured CORS origins:")
        for origin in settings.BACKEND_CORS_ORIGINS:
            print(f"     - {origin}")
    except Exception as e:
        print(f"   ❌ Could not load config: {e}")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
    print("\nIf CORS headers are missing, try:")
    print("1. Restart the backend server")
    print("2. Ensure .env file doesn't override BACKEND_CORS_ORIGINS")
    print("3. Check the startup logs for CORS configuration")

if __name__ == "__main__":
    test_cors()

