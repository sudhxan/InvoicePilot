#!/bin/bash

# InvoicePilot Startup Script

echo "Starting InvoicePilot"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run setup test
echo "🧪 Running setup test..."
python test_setup.py

# Start the application
echo "Starting InvoicePilot web application..."
echo "Open your browser and go to: http://localhost:5001"
echo "Press Ctrl+C to stop the application"
echo ""

python app.py
