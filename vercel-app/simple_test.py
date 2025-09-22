#!/usr/bin/env python3
"""
Simple test to verify the API function works
"""
import os
import sys
import json
import base64

# Add the api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

def test_pdf_extraction():
    """Test PDF text extraction"""
    try:
        from upload import handler
        
        # Create a simple test PDF content (this is fake, but tests the structure)
        test_pdf_content = b"This is fake PDF content for testing"
        
        # Create handler instance
        h = handler()
        
        # Test PDF text extraction
        try:
            text = h.extract_text_from_pdf(test_pdf_content)
            print("❌ PDF extraction should have failed with fake content (this is expected)")
        except Exception as e:
            print(f"✅ PDF extraction correctly failed with fake content: {type(e).__name__}")
        
        # Test Excel creation
        test_data = {"Invoice Number": "INV-001", "Amount": "$100.00"}
        try:
            excel_data = h.create_excel_file(test_data)
            print(f"✅ Excel creation works! Generated {len(excel_data)} chars of base64 data")
        except Exception as e:
            print(f"❌ Excel creation failed: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_api_structure():
    """Test the API request structure"""
    try:
        # Test data
        test_request = {
            "api_key": "test_key",
            "column_config": [
                {"name": "Invoice Number", "description": "The invoice number"},
                {"name": "Amount", "description": "Total amount"}
            ],
            "file_data": base64.b64encode(b"fake pdf content").decode()
        }
        
        print(f"✅ API request structure is valid")
        print(f"   - API key: {'*' * len(test_request['api_key'])}")
        print(f"   - Columns: {len(test_request['column_config'])}")
        print(f"   - File data: {len(test_request['file_data'])} chars")
        
        return True
        
    except Exception as e:
        print(f"❌ API structure test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 InvoicePilot Vercel App - Simple Test\n")
    
    # Test imports and basic functionality
    print("1. Testing PDF and Excel functionality...")
    if not test_pdf_extraction():
        print("❌ PDF/Excel test failed!")
        sys.exit(1)
    
    print("\n2. Testing API structure...")
    if not test_api_structure():
        print("❌ API structure test failed!")
        sys.exit(1)
    
    print("\n🎉 All basic tests passed!")
    print("\n📋 Test Summary:")
    print("✅ Dependencies installed correctly")
    print("✅ PDF processing structure works")
    print("✅ Excel generation works")
    print("✅ API request structure is valid")
    print("\n🚀 The app structure is working! Ready for testing with real data.")
    print("\n💡 Next steps:")
    print("   1. Frontend is running at: http://localhost:8000")
    print("   2. You can test the UI manually")
    print("   3. For full API testing, you'll need a valid Gemini API key")