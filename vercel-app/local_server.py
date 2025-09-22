#!/usr/bin/env python3
"""
Local development server that mimics Vercel's behavior
Serves static files from public/ and handles API routes
"""
import os
import sys
import json
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import io

# Add the api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

class VercelMockHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that mimics Vercel's routing"""
    
    def __init__(self, *args, **kwargs):
        # Change to public directory for static file serving
        super().__init__(*args, directory='public', **kwargs)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/upload':
            self.handle_api_upload()
        else:
            self.send_error(404, "Not Found")
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path.startswith('/api/'):
            self.send_error(405, "Method Not Allowed")
        else:
            # Serve static files from public directory
            if self.path == '/':
                self.path = '/index.html'
            super().do_GET()
    
    def handle_api_upload(self):
        """Handle the /api/upload endpoint"""
        try:
            # Import the native PDF API (no dependencies needed!)
            from upload_native_pdf import process_invoice_request
            
            # Get the request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            print(f"🔗 Processing API request ({content_length} bytes)")
            
            # Process the request using the function
            result = process_invoice_request(post_data)
            
            # Extract status code (default to 200)
            status_code = result.pop('status', 200)
            
            # Send the response
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Send the response data
            response_json = json.dumps(result).encode('utf-8')
            self.wfile.write(response_json)
            
            # Log the result
            if result.get('success'):
                print(f"✅ API Success: {result.get('message', 'Request processed')}")
            else:
                print(f"⚠️ API Error: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            # Send error response
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = json.dumps({
                "error": f"Server error: {str(e)}",
                "type": type(e).__name__
            }).encode('utf-8')
            
            self.wfile.write(error_response)
            
            # Print error for debugging
            print(f"❌ Server Error: {e}")
            import traceback
            traceback.print_exc()
    
    def log_message(self, format, *args):
        """Custom log format"""
        message = format % args
        if '/api/' in message:
            print(f"🔗 API: {message}")
        else:
            print(f"📁 Static: {message}")

def start_server(port=8000):
    """Start the local development server"""
    
    # Ensure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check if public directory exists
    if not os.path.exists('public'):
        print("❌ Error: public/ directory not found!")
        print("   Make sure you're running this from the vercel-app directory")
        sys.exit(1)
    
    # Check if API directory exists
    if not os.path.exists('api'):
        print("❌ Error: api/ directory not found!")
        print("   Make sure you're running this from the vercel-app directory")
        sys.exit(1)
    
    print("🚀 InvoicePilot Local Development Server")
    print("="*50)
    print(f"📁 Serving static files from: {os.path.join(script_dir, 'public')}")
    print(f"🔗 API endpoint available at: /api/upload")
    print(f"🌐 Server running at: http://localhost:{port}")
    print("="*50)
    print("📋 Available routes:")
    print("   GET  /              → Frontend (index.html)")
    print("   GET  /index.html    → Frontend")
    print("   POST /api/upload    → Invoice processing API")
    print("   OPTIONS /api/upload → CORS preflight")
    print("="*50)
    print("💡 Open http://localhost:8000 to test the app!")
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
    # Start the server
    with socketserver.TCPServer(("", port), VercelMockHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    start_server()