# InvoicePilot Quick Start Guide 

## What is InvoicePilot?

InvoicePilot is a powerful web application that uses AI (currently featuring Gemini AI) to extract data from PDF invoices and export it to Excel files with custom column configurations.

## Features

- 📄 **PDF Invoice Processing**: Upload PDF invoices up to 16MB
- 🤖 **AI-Powered Extraction**: Uses Gemini for intelligent data extraction
- 📊 **Custom Excel Export**: Define your own column names and descriptions
- 🖼️ **Multi-Modal Processing**: Sends both PDF and image versions to Gemini for better accuracy
- 🔑 **API Key Management**: Secure API key input and validation
- 🎨 **UI**: Responsive web interface

## Quick Start (3 Steps)

### 1. Get Your Gemini API Key it's FREE.
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Copy the API key (you'll need it in step 3)

### 2. Start the Application
```bash
# Option A: Use the startup script (recommended)
./start.sh

# Option B: Manual start
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### 3. Use the Web Interface
1. Open your browser and go to: **http://localhost:5001**
2. Enter your Gemini API key
3. Configure your Excel columns (add column names and descriptions)
4. Upload a PDF invoice
5. Click "Extract Invoice Data"
6. Download the generated Excel file

## Example Column Configuration

| Column Name | Description |
|-------------|-------------|
| Invoice Number | The unique invoice number or reference |
| Invoice Date | The date when the invoice was issued |
| Due Date | The payment due date |
| Vendor Name | The name of the company who issued the invoice |
| Customer Name | The name of the customer or recipient |
| Total Amount | The total amount due on the invoice |
| Tax Amount | The tax amount included in the total |
| Currency | The currency used (USD, EUR, etc.) |

## File Structure

```
InvoicePilot/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── start.sh              # Quick start script
├── demo.py               # API demonstration script
├── test_setup.py         # Setup verification script
├── templates/
│   └── index.html        # Web interface
├── uploads/              # Temporary PDF storage
├── outputs/              # Generated Excel files
├── venv/                 # Virtual environment
├── README.md             # Full documentation
└── QUICK_START.md        # This file
```

## Troubleshooting

### Common Issues:

1. **"Address already in use"**
   - The default port 5000 is in use
   - The app automatically uses port 5001 instead

2. **"Failed to convert PDF to image"**
   - Make sure poppler-utils is installed:
   - macOS: `brew install poppler`
   - Ubuntu/Debian: `sudo apt-get install poppler-utils`

3. **"Gemini API error"**
   - Verify your API key is correct
   - Check if you have sufficient API quota

4. **"No valid JSON found in response"**
   - The AI might not have found the requested data
   - Try adjusting your column descriptions to be more specific

## API Usage

You can also use InvoicePilot programmatically:

```python
import requests

# Upload and process an invoice
files = {'file': open('invoice.pdf', 'rb')}
data = {
    'api_key': 'YOUR_GEMINI_API_KEY',
    'column_config': json.dumps([
        {'name': 'Invoice Number', 'description': 'The unique invoice number'},
        {'name': 'Total Amount', 'description': 'The total amount due'}
    ])
}

response = requests.post('http://localhost:5001/upload', files=files, data=data)
result = response.json()
```

## Support

- Check the full [README.md](README.md) for detailed documentation
- Run `python test_setup.py` to verify your setup
- Use `python demo.py` to test the API programmatically

## Next Steps

1. **Customize Columns**: Add your specific invoice fields
2. **Batch Processing**: Upload multiple invoices
3. **Integration**: Use the API in your own applications
4. **Advanced Features**: Explore the full documentation

---

**Happy Invoice Processing! 🎉**
