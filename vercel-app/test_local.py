#!/usr/bin/env python3
"""
Simple test script for the Vercel app API
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from upload import handler
from http.server import BaseHTTPRequestHandler
import json
import base64
import io

class MockRequest:
    def __init__(self, data):
        self.data = data
        self.headers = {'Content-Length': str(len(data))}
    
    def read(self, length):
        return self.data

class MockHandler(handler):
    def __init__(self, request_data):
        self.rfile = MockRequest(request_data)
        self.response_data = None
        self.response_code = None
        self.response_headers = {}
    
    def send_response(self, code):
        self.response_code = code
    
    def send_header(self, name, value):
        self.response_headers[name] = value
    
    def end_headers(self):
        pass
    
    def wfile_write(self, data):
        self.response_data = data

def test_api():
    """Test the API with sample data"""
    
    # Create sample test data
    test_data = {
        "api_key": "test_key_12345",  # This won't work with real Gemini, but tests structure
        "column_config": [
            {"name": "Invoice Number", "description": "The invoice number or ID"},
            {"name": "Date", "description": "Invoice date"},
            {"name": "Total Amount", "description": "Total invoice amount"}
        ],
        "file_data": "data:application/pdf;base64," + base64.b64encode(b"This is not a real PDF but will test the structure").decode()
    }
    
    # Convert to JSON bytes
    json_data = json.dumps(test_data).encode('utf-8')
    
    # Create mock handler
    mock_handler = MockHandler(json_data)
    
    # Override wfile.write method
    mock_handler.wfile = type('MockFile', (), {
        'write': lambda self, data: setattr(mock_handler, 'response_data', data)
    })()
    
    print("🧪 Testing API structure...")
    print("📋 Test data prepared")
    print(f"   - API Key: {test_data['api_key'][:10]}...")
    print(f"   - Columns: {len(test_data['column_config'])}")
    print(f"   - File data: {len(test_data['file_data'])} chars")
    
    try:
        # Test the API
        mock_handler.do_POST()
        
        print("\n✅ API structure test completed!")
        print(f"📤 Response code: {mock_handler.response_code}")
        
        if mock_handler.response_data:
            try:
                response = json.loads(mock_handler.response_data.decode('utf-8'))
                print("📋 Response structure:")
                for key in response.keys():
                    print(f"   - {key}: {type(response[key]).__name__}")
            except:
                print("📋 Response (raw):", mock_handler.response_data[:200])
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_dependencies():
    """Test that all dependencies are working"""
    print("🔍 Testing dependencies...")
    
    try:
        import google.generativeai as genai
        print("✅ google-generativeai: OK")
    except ImportError as e:
        print(f"❌ google-generativeai: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas: OK")
    except ImportError as e:
        print(f"❌ pandas: {e}")
        return False
    
    try:
        import PyPDF2
        print("✅ PyPDF2: OK")
    except ImportError as e:
        print(f"❌ PyPDF2: {e}")
        return False
    
    try:
        import openpyxl
        print("✅ openpyxl: OK")
    except ImportError as e:
        print(f"❌ openpyxl: {e}")
        return False
    
    return True

def start_simple_server():
    """Start a simple HTTP server for testing"""
    import http.server
    import socketserver
    import threading
    import time
    
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def do_POST(self):
            if self.path == '/api/upload':
                # Handle API request
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # Create handler instance
                api_handler = handler()
                api_handler.rfile = io.BytesIO(post_data)
                api_handler.headers = self.headers
                
                # Capture response
                response_data = None
                response_code = 200
                
                class MockWFile:
                    def __init__(self):
                        self.data = b''
                    def write(self, data):
                        self.data += data
                
                mock_wfile = MockWFile()
                api_handler.wfile = mock_wfile
                api_handler.send_response = lambda code: setattr(self, '_code', code)
                api_handler.send_header = lambda name, value: None
                api_handler.end_headers = lambda: None
                
                try:
                    api_handler.do_POST()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(mock_wfile.data)
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
            else:
                super().do_POST()
        
        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
    
    # Change to public directory
    os.chdir('public')
    
    PORT = 8000
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"\n🚀 Test server starting on http://localhost:{PORT}")
        print("📁 Serving from public/ directory")
        print("🔗 API available at http://localhost:8000/api/upload")
        print("\n💡 Open http://localhost:8000 in your browser to test!")
        print("⏹️  Press Ctrl+C to stop the server\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    print("🧪 InvoicePilot Vercel App - Local Test\n")
    
    # Test dependencies
    if not test_dependencies():
        print("\n❌ Dependency test failed!")
        sys.exit(1)
    
    print("\n" + "="*50)
    
    # Test API structure
    if not test_api():
        print("\n❌ API test failed!")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("\n🎉 All tests passed! Starting test server...")
    
    # Start test server
    start_simple_server()