# InvoicePilot

Open sourced web application that extracts data from PDF invoices using AI (currently featuring Google's Gemini AI) and exports the results to Excel files with custom column configurations you would like to extract it as.


## Features

- 📄 **PDF Invoice Upload**: Upload PDF invoices
- 🤖 **AI-Powered Extraction**: Uses Gemini 2.5 Pro for intelligent data extraction
- 📊 **Custom Excel Export**: Define your own column names and descriptions
- 🖼️ **Multi-Modal Processing**: Sends both PDF and image versions to Gemini for better accuracy
- 🔑 **API Key Management**: Secure API key input and validation
- 🎨 **UI**: Responsive web interface

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key
- poppler-utils (for PDF to image conversion)

### Installing poppler-utils

**macOS:**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**Windows:**
Download from [poppler-windows](https://github.com/oschwartz10612/poppler-windows) and add to PATH.

## Installation

1. **Clone or download the project**
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open your browser and go to:**
   ```
   http://localhost:5001
   ```

## Usage

1. **Enter your Gemini API Key** in the configuration section
2. **Configure Excel columns** by adding column names and descriptions for the data you want to extract
3. **Upload a PDF invoice** by clicking the upload area or dragging and dropping
4. **Click "Extract Invoice Data"** to process the invoice
5. **Download the Excel file** with the extracted data

## API Key Setup

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key, it's FREE.
3. Copy the API key and paste it into the application

## Column Configuration

Define custom columns for your Excel output:

- **Column Name**: The exact name that will appear in the Excel file
- **Description**: A detailed description of what data to extract for this column

### Example Column Configurations:

| Column Name | Description |
|-------------|-------------|
| Invoice Number | The unique invoice number or reference |
| Invoice Date | The date when the invoice was issued |
| Due Date | The payment due date |
| Vendor Name | The name of the company or person who issued the invoice |
| Customer Name | The name of the customer or recipient |
| Total Amount | The total amount due on the invoice |
| Tax Amount | The tax amount included in the total |
| Currency | The currency used (USD, EUR, etc.) |
| Payment Terms | Payment terms like "Net 30", "Due on receipt", etc. |
| Line Items | Description of products or services |

## How It Works

1. **PDF Processing**: The uploaded PDF is converted to a high-resolution image using pdf2image
2. **AI Analysis**: Both the original PDF and the converted image are sent to Gemini 2.5 Pro
3. **Data Extraction**: Gemini analyzes the invoice and extracts data based on your column descriptions
4. **Excel Generation**: The extracted data is formatted into an Excel file with your custom columns
5. **Download**: The Excel file is generated and made available for download

## File Structure

```
InvoicePilot/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface
├── uploads/              # Temporary PDF storage
├── outputs/              # Generated Excel files
└── README.md            # This file
```

## Troubleshooting

### Common Issues:

1. **"Failed to convert PDF to image"**
   - Ensure poppler-utils is installed correctly
   - Check if the PDF file is corrupted

2. **"Gemini API error"**
   - Verify your API key is correct
   - Check if you have sufficient API quota

3. **"No valid JSON found in response"**
   - The AI might not have found the requested data
   - Try adjusting your column descriptions to be more specific

### Performance Tips:

- Use high-quality PDF files for better extraction accuracy
- Be specific in your column descriptions
- For large invoices, consider splitting into smaller sections

## Security Notes

- API keys are not stored permanently
- Uploaded files are automatically deleted after processing
- The application runs locally on your machine

## License

This project is open source and available under the MIT License.

## Support

For issues or questions, please check the troubleshooting section or create an issue in the project repository.
