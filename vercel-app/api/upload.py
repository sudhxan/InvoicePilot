from http.server import BaseHTTPRequestHandler
import json
import base64
import io
import tempfile
import os
from datetime import datetime
import google.generativeai as genai
import pandas as pd
import PyPDF2
from PIL import Image
import requests

# Import the native PDF processing function
import sys
sys.path.insert(0, os.path.dirname(__file__))
from upload_native_pdf import process_invoice_request

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Set CORS headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()

            # Get content length
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Use the native PDF processing function
            result = process_invoice_request(post_data)
            
            # Extract status code (default to 200)
            status_code = result.pop('status', 200)
            
            # Send the response
            if status_code != 200:
                self.send_response(status_code)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Server error: {e}"}).encode())

    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def extract_text_from_pdf(self, pdf_bytes):
        """Extract text from PDF using PyPDF2"""
        text = ""
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
                
        except Exception as e:
            raise Exception(f"PDF text extraction failed: {e}")
        
        return text

    def extract_invoice_data_with_gemini(self, api_key, pdf_text, column_config):
        """Extract invoice data using Gemini AI"""
        try:
            # Configure Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # Prepare column descriptions for the prompt
            column_descriptions = []
            for col in column_config:
                column_descriptions.append(f"- {col['name']}: {col['description']}")
            
            column_descriptions_text = "\n".join(column_descriptions)
            
            # Create the prompt
            prompt = f"""
            You are an expert at extracting data from invoices. Please analyze the provided invoice text and extract the following information:

            {column_descriptions_text}

            Please return the data in JSON format with the exact column names provided above. If any information is not found, use null for that field.

            Example format:
            {{
                "column_name_1": "extracted_value_1",
                "column_name_2": "extracted_value_2"
            }}

            Invoice text:
            {pdf_text}

            Extract the data now:
            """
            
            # Generate response
            response = model.generate_content(prompt)
            
            # Parse the JSON response
            try:
                # Extract JSON from the response text
                response_text = response.text
                # Find JSON in the response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_str = response_text[start_idx:end_idx]
                    extracted_data = json.loads(json_str)
                    return extracted_data
                else:
                    return {"error": "No valid JSON found in response"}
                    
            except json.JSONDecodeError as e:
                return {"error": f"Failed to parse JSON response: {e}"}
                
        except Exception as e:
            return {"error": f"Gemini API error: {e}"}

    def create_excel_file(self, extracted_data):
        """Create Excel file and return as base64"""
        try:
            df = pd.DataFrame([extracted_data])
            
            # Create Excel file in memory
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_buffer.seek(0)
            
            # Convert to base64
            excel_base64 = base64.b64encode(excel_buffer.getvalue()).decode('utf-8')
            return excel_base64
            
        except Exception as e:
            raise Exception(f"Excel creation failed: {e}")