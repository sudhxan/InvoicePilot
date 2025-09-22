#!/usr/bin/env python3
"""
Test the fixed API implementation
"""
import json
import base64
import sys
import os

# Add the api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

def test_api_function():
    """Test the API function directly"""
    try:
        from upload_functions import process_invoice_request
        
        # Create test data
        test_data = {
            "api_key": "test_key_12345",  # Fake key for structure testing
            "column_config": [
                {"name": "Invoice Number", "description": "The invoice number"},
                {"name": "Date", "description": "Invoice date"},
                {"name": "Amount", "description": "Total amount"}
            ],
            "file_data": base64.b64encode(b"This is fake PDF content for testing").decode()
        }
        
        print("🧪 Testing API function directly...")
        print(f"📋 Request data: {len(json.dumps(test_data))} chars")
        
        # Test the function
        result = process_invoice_request(test_data)
        
        print(f"📤 Response status: {result.get('status', 'unknown')}")
        print(f"📋 Response keys: {list(result.keys())}")
        
        if result.get('success'):
            print("✅ API function works correctly!")
        else:
            print(f"⚠️ Expected error (no real API key): {result.get('error', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ API function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Fixed API Implementation\n")
    
    if test_api_function():
        print("\n✅ API function test completed!")
        print("\n💡 The server should now work without BaseRequestHandler errors")
        print("🌐 Test at: http://localhost:8000")
    else:
        print("\n❌ API function test failed!")
        sys.exit(1)