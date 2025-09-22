"""
Function-based API for invoice processing (not class-based)
This avoids the BaseRequestHandler instantiation issues
"""
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

def extract_text_from_pdf(pdf_bytes):
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

def extract_invoice_data_with_gemini(api_key, pdf_text, column_config):
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

def create_excel_file(extracted_data):
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

def process_invoice_request(request_data):
    """Main function to process invoice request"""
    try:
        # Parse request data
        if isinstance(request_data, bytes):
            data = json.loads(request_data.decode('utf-8'))
        else:
            data = request_data
        
        api_key = data.get('api_key')
        column_config = data.get('column_config', [])
        file_data = data.get('file_data')
        
        # Validate inputs
        if not api_key:
            return {"error": "API key is required", "status": 400}
        
        if not column_config:
            return {"error": "Column configuration is required", "status": 400}
        
        if not file_data:
            return {"error": "No file data provided", "status": 400}

        # Decode base64 PDF data
        try:
            pdf_bytes = base64.b64decode(file_data.split(',')[1] if ',' in file_data else file_data)
        except Exception as e:
            return {"error": f"Invalid file data: {e}", "status": 400}

        # Extract text from PDF
        try:
            pdf_text = extract_text_from_pdf(pdf_bytes)
            if not pdf_text.strip():
                return {"error": "Could not extract text from PDF. Please ensure the PDF contains readable text.", "status": 400}
        except Exception as e:
            return {"error": f"PDF processing error: {e}", "status": 500}

        # Extract data using Gemini
        try:
            extracted_data = extract_invoice_data_with_gemini(api_key, pdf_text, column_config)
            if "error" in extracted_data:
                return {"error": extracted_data["error"], "status": 500}
        except Exception as e:
            return {"error": f"AI extraction error: {e}", "status": 500}

        # Create Excel file
        try:
            excel_data = create_excel_file(extracted_data)
            excel_filename = f"invoice_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            response = {
                "success": True,
                "message": "Invoice data extracted successfully",
                "extracted_data": extracted_data,
                "excel_file": excel_filename,
                "excel_data": excel_data,
                "status": 200
            }
            
            return response
            
        except Exception as e:
            return {"error": f"Excel generation error: {e}", "status": 500}

    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON in request: {e}", "status": 400}
    except Exception as e:
        return {"error": f"Server error: {e}", "status": 500}