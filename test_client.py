#!/usr/bin/env python3
"""
Simple test client for the Q/A Maker backend
"""

import requests
import json
import io
import os

# Run this in a Python shell in your project directory
import os
from dotenv import load_dotenv


def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get('http://localhost:5000/health')
        print(f"Health Check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_upload_info():
    """Test the upload info endpoint"""
    try:
        response = requests.get('http://localhost:5000/upload-info')
        print(f"Upload Info: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Upload info failed: {e}")
        return False

def get_sample_csv_path():
    """Get the path to the specific CSV file"""
    return r"C:\Users\Prashant.Kumar\Downloads\sample_CSV\timesheet.csv"

def test_chat_endpoint():
    """Test the chat endpoint with sample data from local CSV file"""
    try:
        # Get the specific CSV file path
        csv_path = get_sample_csv_path()
        
        # Check if file exists
        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            return False
        
        # Open and send the file directly
        with open(csv_path, 'rb') as csv_file:
            files = {'file': (os.path.basename(csv_path), csv_file, 'text/csv')}
            data = {'question': 'Show me the total effort logged by Prashant Kumar this week.?'}
            
            response = requests.post('http://localhost:5000/chat', files=files, data=data)
            print(f"Chat Test: {response.status_code}")
            print(f"Using CSV file: {csv_path}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Question: {result.get('question')}")
                print(f"Answer: {result.get('answer')}")
                print(f"CSV Info: {result.get('csv_rows')} rows, {len(result.get('csv_columns', []))} columns")
            else:
                print(f"Error Response: {response.json()}")
                
            return response.status_code == 200
            
    except Exception as e:
        print(f"Chat test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Q/A Maker Backend")
    print("=" * 40)
    
    print("\n1. Testing Health Check...")
    health_ok = test_health_check()
    
    print("\n2. Testing Upload Info...")
    upload_info_ok = test_upload_info()
    
    print("\n3. Testing Chat Endpoint...")
    chat_ok = test_chat_endpoint()
    
    print("\n" + "=" * 40)
    print("Test Results:")
    print(f"Health Check: {'✓' if health_ok else '✗'}")
    print(f"Upload Info: {'✓' if upload_info_ok else '✗'}")
    print(f"Chat Endpoint: {'✓' if chat_ok else '✗'}")
    
    if all([health_ok, upload_info_ok, chat_ok]):
        print("\nAll tests passed! 🎉")
    else:
        print("\nSome tests failed. Check your configuration and ensure the server is running.")

if __name__ == '__main__':
    main()