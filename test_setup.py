#!/usr/bin/env python3
"""
Test script to verify InvoicePilot setup
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import flask
        print(" Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import google.generativeai
        print(" Google Generative AI imported successfully")
    except ImportError as e:
        print(f"❌ Google Generative AI import failed: {e}")
        return False
    
    try:
        from pdf2image import convert_from_path
        print(" pdf2image imported successfully")
    except ImportError as e:
        print(f"❌ pdf2image import failed: {e}")
        return False
    
    try:
        import pandas
        print(" Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import openpyxl
        print(" OpenPyXL imported successfully")
    except ImportError as e:
        print(f"❌ OpenPyXL import failed: {e}")
        return False
    
    return True

def test_directories():
    """Test if required directories exist"""
    required_dirs = ['uploads', 'outputs', 'templates']
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f" Directory '{dir_name}' exists")
        else:
            print(f"Directory '{dir_name}' missing")
            return False
    
    return True

def test_files():
    """Test if required files exist"""
    required_files = ['app.py', 'requirements.txt', 'templates/index.html']
    
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f" File '{file_name}' exists")
        else:
            print(f"File '{file_name}' missing")
            return False
    
    return True

def main():
    print("InvoicePilot Setup Test")
    print("=" * 40)
    
    all_tests_passed = True
    
    print("\nTesting imports...")
    if not test_imports():
        all_tests_passed = False
    
    print("\nTesting directories...")
    if not test_directories():
        all_tests_passed = False
    
    print("\nTesting files...")
    if not test_files():
        all_tests_passed = False
    
    print("\n" + "=" * 40)
    if all_tests_passed:
        print("🎉 All tests passed! InvoicePilot is ready to run.")
        print("\nTo start the application, run:")
        print("python app.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
