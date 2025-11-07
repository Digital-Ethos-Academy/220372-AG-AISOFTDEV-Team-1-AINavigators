"""Test script to verify .env file is loaded correctly."""

import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("Testing .env File Loading")
print("=" * 60)

# Test 1: Check current working directory
print(f"\n1. Current working directory: {os.getcwd()}")

# Test 2: Check if .env exists
env_path = Path(".env")
print(f"\n2. .env file exists in current dir: {env_path.exists()}")
if env_path.exists():
    print(f"   Path: {env_path.absolute()}")

# Test 3: Load dotenv explicitly
from dotenv import load_dotenv
load_dotenv()
print("\n3. load_dotenv() called")

# Test 4: Check if GOOGLE_API_KEY is loaded
api_key = os.getenv("GOOGLE_API_KEY")
print(f"\n4. GOOGLE_API_KEY loaded: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"   Key starts with: {api_key[:20]}..." if len(api_key) > 20 else f"   Key: {api_key}")
else:
    print("   ERROR: API key not found!")

# Test 5: Try importing gemini module
print("\n5. Testing gemini module import...")
try:
    from app.services.ai import gemini
    print("   ✅ Gemini module imported successfully")
    
    # Test 6: Try to initialize client
    print("\n6. Testing Gemini client initialization...")
    try:
        from app.services.ai.gemini import _ensure_client
        client = _ensure_client()
        print("   ✅ Gemini client initialized successfully!")
    except Exception as e:
        print(f"   ❌ Failed to initialize client: {e}")
        
except Exception as e:
    print(f"   ❌ Failed to import: {e}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)

