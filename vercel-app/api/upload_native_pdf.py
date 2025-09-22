"""
Native PDF processing - Send PDF directly to Gemini (no image conversion needed!)
This works perfectly on Vercel with no system dependencies
"""
import json
import base64
import io
from datetime import datetime
import google.generativeai as genai
import pandas as pd
import PyPDF2

def extract_text_from_pdf(pdf_bytes):
    """Extract text from PDF using PyPDF2 (for fallback)"""
    text = ""
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
            
    except Exception as e:
        raise Exception(f"PDF text extraction failed: {e}")
    
    return text

def extract_invoice_data_with_gemini_native_pdf(api_key, pdf_base64, pdf_text_fallback, column_config):
    """
    Extract invoice data using Gemini with NATIVE PDF support
    Sends PDF directly to Gemini - no image conversion needed!
    """
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Prepare column descriptions for the prompt
        column_descriptions = []
        for col in column_config:
            column_descriptions.append(f"- {col['name']}: {col['description']}")
        
        column_descriptions_text = "\n".join(column_descriptions)
        
        # Create the prompt for PDF analysis
        prompt = f"""
        You are an expert at extracting data from invoices. Please analyze the provided PDF invoice and extract the following information:

        {column_descriptions_text}

        Please return the data in JSON format with the exact column names provided above. If any information is not found, use null for that field.

        Example format:
        {{
            "column_name_1": "extracted_value_1",
            "column_name_2": "extracted_value_2"
        }}

        Please analyze the PDF document thoroughly, including any visual elements, tables, and formatting that might contain relevant information.
        
        Extract the data now:
        """
        
        # Prepare the content for Gemini with native PDF support
        content = [prompt]
        
        # Try to send PDF directly to Gemini
        try:
            content.append({
                "mime_type": "application/pdf",
                "data": pdf_base64
            })
            
            print("✅ Using native PDF processing mode")
            
            # Generate response with PDF
            response = model.generate_content(content)
            
        except Exception as pdf_error:
            print(f"⚠️ Native PDF processing failed: {pdf_error}")
            print("🔄 Falling back to text-only mode...")
            
            # Fallback to text-only processing
            text_prompt = f"""
            You are an expert at extracting data from invoices. Please analyze the provided invoice text and extract the following information:

            {column_descriptions_text}

            Please return the data in JSON format with the exact column names provided above. If any information is not found, use null for that field.

            Example format:
            {{
                "column_name_1": "extracted_value_1",
                "column_name_2": "extracted_value_2"
            }}

            Invoice text:
            {pdf_text_fallback}

            Extract the data now:
            """
            
            response = model.generate_content([text_prompt])
        
        # Parse the JSON response
        try:
            # Extract JSON from the response text
            response_text = response.text
            print(f"📋 Gemini response length: {len(response_text)} chars")
            
            # Find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                extracted_data = json.loads(json_str)
                print(f"✅ Successfully extracted {len(extracted_data)} fields")
                return extracted_data
            else:
                return {"error": "No valid JSON found in response", "raw_response": response_text[:500]}
                
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse JSON response: {e}", "raw_response": response_text[:500]}
            
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
    """
    Main function to process invoice request with NATIVE PDF processing
    No system dependencies required - works perfectly on Vercel!
    """
    try:
        # Parse request data
        if isinstance(request_data, bytes):
            data = json.loads(request_data.decode('utf-8'))
        else:
            data = request_data
        
        api_key = data.get('api_key')
        column_config = data.get('column_config', [])
        file_data = data.get('file_data')
        
        print("🚀 Starting native PDF processing...")
        
        # Validate inputs
        if not api_key:
            return {"error": "API key is required", "status": 400}
        
        if not column_config:
            return {"error": "Column configuration is required", "status": 400}
        
        if not file_data:
            return {"error": "No file data provided", "status": 400}

        # Extract base64 PDF data
        try:
            if ',' in file_data:
                pdf_base64 = file_data.split(',')[1]  # Remove data:application/pdf;base64, prefix
            else:
                pdf_base64 = file_data
            
            # Decode to verify it's valid
            pdf_bytes = base64.b64decode(pdf_base64)
            print(f"📄 PDF size: {len(pdf_bytes)} bytes")
            
        except Exception as e:
            return {"error": f"Invalid PDF data: {e}", "status": 400}

        # Extract text as fallback (in case native PDF fails)
        pdf_text_fallback = ""
        try:
            pdf_text_fallback = extract_text_from_pdf(pdf_bytes)
            print(f"📝 Extracted text length: {len(pdf_text_fallback)} chars")
        except Exception as e:
            print(f"⚠️ Text extraction failed: {e}")

        # Process with Gemini using native PDF support
        try:
            extracted_data = extract_invoice_data_with_gemini_native_pdf(
                api_key, pdf_base64, pdf_text_fallback, column_config
            )
            
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
                "message": "Invoice data extracted successfully (native PDF processing)",
                "extracted_data": extracted_data,
                "excel_file": excel_filename,
                "excel_data": excel_data,
                "processing_mode": "native_pdf",
                "status": 200
            }
            
            print("✅ Processing completed successfully!")
            return response
            
        except Exception as e:
            return {"error": f"Excel generation error: {e}", "status": 500}

    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON in request: {e}", "status": 400}
    except Exception as e:
        return {"error": f"Server error: {e}", "status": 500}