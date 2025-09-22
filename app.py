from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile
import json
from werkzeug.utils import secure_filename
import google.generativeai as genai
from pdf2image import convert_from_path
from PIL import Image
import pandas as pd
import io
import base64
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def pdf_to_image(pdf_path):
    """Convert PDF to image using pdf2image"""
    try:
        images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=1)
        if images:
            return images[0]
        return None
    except Exception as e:
        print(f"Error converting PDF to image: {e}")
        return None

def encode_image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

def extract_invoice_data_with_gemini(api_key, pdf_path, image, column_config):
    """Extract invoice data using Gemini 2.5 Pro"""
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
        You are an expert at extracting data from invoices. Please analyze the provided invoice (both PDF and image versions) and extract the following information:

        {column_descriptions_text}

        Please return the data in JSON format with the exact column names provided above. If any information is not found, use null for that field.

        Example format:
        {{
            "column_name_1": "extracted_value_1",
            "column_name_2": "extracted_value_2",
            ...
        }}

        Extract the data now:
        """
        
        # Prepare the content for Gemini
        content = [prompt]
        
        # Add image if available
        if image:
            img_base64 = encode_image_to_base64(image)
            content.append({
                "mime_type": "image/png",
                "data": img_base64
            })
        
        # Generate response
        response = model.generate_content(content)
        
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Get form data
        api_key = request.form.get('api_key')
        column_config = json.loads(request.form.get('column_config', '[]'))
        
        if not api_key:
            return jsonify({"error": "API key is required"}), 400
        
        if not column_config:
            return jsonify({"error": "Column configuration is required"}), 400
        
        # Check if file is uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Convert PDF to image
            image = pdf_to_image(file_path)
            if not image:
                return jsonify({"error": "Failed to convert PDF to image"}), 500
            
            # Extract data using Gemini
            extracted_data = extract_invoice_data_with_gemini(api_key, file_path, image, column_config)
            
            if "error" in extracted_data:
                return jsonify(extracted_data), 500
            
            # Create Excel file
            df = pd.DataFrame([extracted_data])
            excel_filename = f"invoice_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            excel_path = os.path.join(app.config['OUTPUT_FOLDER'], excel_filename)
            df.to_excel(excel_path, index=False)
            
            # Clean up uploaded file
            os.remove(file_path)
            
            return jsonify({
                "success": True,
                "message": "Invoice data extracted successfully",
                "extracted_data": extracted_data,
                "excel_file": excel_filename
            })
        
        return jsonify({"error": "Invalid file type"}), 400
        
    except Exception as e:
        return jsonify({"error": f"Server error: {e}"}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Download error: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
