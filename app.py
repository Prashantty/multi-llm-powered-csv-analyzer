from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import requests
from dotenv import load_dotenv
import json
import base64
from io import BytesIO

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configuration for external LLM API
LLM_API_BASE_URL = os.getenv("LLM_API_BASE_URL")  # e.g., https://api.anthropic.com/v1/messages
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-3-sonnet-20240229")  # Default to Claude Sonnet
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB


load_dotenv()
print("Anthropic key exists:", os.getenv("ANTHROPIC_API_KEY"))
print("OpenAI key exists:", bool(os.getenv("OPENAI_API_KEY")))

# Supported LLM providers
SUPPORTED_PROVIDERS = {
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1/messages",
        "supports_files": True,
        "file_types": ["text/csv", "application/vnd.ms-excel"]
    },
    "openai": {
        "base_url": "https://api.openai.com/v1/chat/completions",
        "supports_files": True,
        "file_types": ["text/csv"]
    },
    "google": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/models",
        "supports_files": True,
        "file_types": ["text/csv"]
    }
}

# Token limits for different models
TOKEN_LIMITS = {
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4o": 50000,
    "gpt-4-turbo": 128000,
    "gpt-35-turbo": 4096,
    "gpt-35-turbo-16k": 16385
}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Flask app is running"})

@app.route('/chat', methods=['POST'])
def chat():
    """
    Process Q/A request with CSV file
    Expects:
    - 'file': CSV file
    - 'question': Question to ask about the CSV data
    """
    try:
        # Validate request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        if 'question' not in request.form:
            return jsonify({"error": "No question provided"}), 400
        
        file = request.files['file']
        question = request.form['question']
        
        # Validate file
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({"error": "Only CSV files are supported"}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({"error": "File size exceeds 16MB limit"}), 400
        
        # Get file content as bytes without processing
        file_content = file.read()
        file.seek(0)  # Reset for potential future use
        
        # Determine LLM provider and call appropriate API
        provider = determine_llm_provider()
        
        try:
            if provider == "azure_openai":
                # Azure OpenAI: Extract content first, then send
                result = call_azure_openai_api(file_content, file.filename, question)
                processing_method = "extracted_content"
            elif provider == "anthropic":
                # Anthropic: Direct file upload (no extraction)
                result = call_anthropic_api(file_content, file.filename, question)
                processing_method = "direct_file_upload"
            elif provider == "openai":
                result = call_openai_api(file_content, file.filename, question)
                processing_method = "text_extraction"
            elif provider == "google":
                result = call_google_api(file_content, file.filename, question)
                processing_method = "text_extraction"
            else:
                return jsonify({"error": "No supported LLM provider configured"}), 500
            
            # Add processing method to response
            result["processing_info"]["processing_method"] = processing_method
            
            return jsonify({
                "success": True,
                "question": question,
                "answer": result["answer"],
                "file_name": file.filename,
                "file_size": file_size,
                "csv_rows": result.get("processing_info", {}).get("data_rows", "unknown"),
                "csv_columns": result.get("processing_info", {}).get("data_columns", []),
                "processing_info": result.get("processing_info", {}),
                "provider_used": provider
            })
            
        except Exception as e:
            return jsonify({"error": f"Error calling LLM API: {str(e)}"}), 500
        
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

def determine_llm_provider():
    """Determine which LLM provider to use based on environment variables"""
    if os.getenv("AZURE_OPENAI_API_KEY"):
        return "azure_openai"
    elif os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    elif os.getenv("OPENAI_API_KEY"):
        return "openai"
    elif os.getenv("GOOGLE_API_KEY"):
        return "google"
    else:
        return None

def call_anthropic_api(file_content, filename, question):
    """Call Anthropic Claude API with file content"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise Exception("ANTHROPIC_API_KEY not found in environment variables")
    
    # Encode file content to base64
    file_base64 = base64.b64encode(file_content).decode('utf-8')
    
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
        "max_tokens": 1500,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"I have uploaded a CSV file named '{filename}'. Please analyze this data and answer the following question: {question}"
                    },
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "text/csv",
                            "data": file_base64
                        }
                    }
                ]
            }
        ]
    }
    
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=payload,
        timeout=60
    )
    
    if response.status_code != 200:
        raise Exception(f"Anthropic API error: {response.status_code} - {response.text}")
    
    result = response.json()
    return {
        "answer": result["content"][0]["text"],
        "processing_info": {
            "model": payload["model"],
            "provider": "anthropic",
            "tokens_used": result.get("usage", {})
        }
    }

def call_azure_openai_api(file_content, filename, question):
    """Call Azure OpenAI API with extracted file content - FULL CONTENT EXTRACTION"""
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    if not api_key or not endpoint:
        raise Exception("AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT required")
    
    # Initialize variables
    csv_rows = "unknown"
    csv_columns = []
    
    # For Azure OpenAI: Extract and process FULL CSV content
    try:
        import pandas as pd
        from io import BytesIO
        
        # Read CSV and extract structured data
        df = pd.read_csv(BytesIO(file_content))
        csv_rows = len(df)
        csv_columns = df.columns.tolist()
        
        # Create FULL data summary - NO TRUNCATION
        print(f"📊 Processing full CSV content: {csv_rows} rows, {len(csv_columns)} columns")
        
        # Convert entire dataframe to string representation
        full_data_string = df.to_string(index=False)
        
        # Get complete data types and statistics
        data_types_string = df.dtypes.to_string()
        basic_stats_string = df.describe(include='all').to_string()
        
        # Create comprehensive data summary with ALL content
        data_summary = f"""File: {filename}
Total Rows: {csv_rows}
Total Columns: {len(csv_columns)}
Column Names: {csv_columns}

COMPLETE DATA CONTENT:
{full_data_string}

DATA TYPES:
{data_types_string}

COMPLETE STATISTICAL SUMMARY:
{basic_stats_string}
"""
        
        print(f"📝 Full data summary created - Length: {len(data_summary):,} characters")

    except Exception as e:
        print(f"❌ Pandas processing failed: {str(e)}")
        # Fallback to raw text - FULL CONTENT
        try:
            csv_text = file_content.decode('utf-8')
            print(f"📝 Using raw CSV text - Length: {len(csv_text):,} characters")
            
            # Extract ALL content as text
            data_summary = f"""CSV File: {filename}

COMPLETE RAW CSV CONTENT:
{csv_text}
"""
            
            # Try to get basic info from raw text
            lines = csv_text.split('\n')
            if len(lines) > 0:
                csv_columns = [col.strip() for col in lines[0].split(',')]
                csv_rows = len(lines) - 1  # Subtract header row
                
            print(f"📊 Raw processing: {csv_rows} rows, {len(csv_columns)} columns")
            
        except Exception as decode_error:
            raise Exception(f"Unable to process CSV file: {str(decode_error)}")
    
    # Add token counting with the complete data
    print(f"🔍 Starting token analysis for full content...")
    
    # Prepare the complete prompt
    system_prompt = "You are a helpful assistant that analyzes CSV data and answers questions about it. You have been provided with the complete extracted data from a CSV file. Provide detailed, accurate analysis based on ALL the data provided."
    
    user_prompt = f"I have uploaded a CSV file and extracted its COMPLETE contents. Here is the full processed data:\n\n{data_summary}\n\nUser Question: {question}\n\nPlease analyze ALL the data and provide a comprehensive answer to the user's question."
    
    # Count tokens for the complete content
    try:
        import tiktoken
        
        # Get encoding for the model
        if "gpt-4" in deployment_name.lower():
            encoding = tiktoken.encoding_for_model("gpt-4")
        else:
            encoding = tiktoken.encoding_for_model("gpt-4")  # Default
        
        system_tokens = len(encoding.encode(system_prompt))
        user_tokens = len(encoding.encode(user_prompt))
        total_input_tokens = system_tokens + user_tokens + 10  # +10 for message overhead
        
        # Check against model limits
        model_limit = TOKEN_LIMITS.get(deployment_name, 50000)
        max_response_tokens = 2000
        total_tokens_needed = total_input_tokens + max_response_tokens
        
        print(f"📊 Complete Token Analysis:")
        print(f"   System prompt: {system_tokens:,} tokens")
        print(f"   User content (full data + question): {user_tokens:,} tokens")
        print(f"   Total input: {total_input_tokens:,} tokens")
        print(f"   Response reserve: {max_response_tokens:,} tokens")
        print(f"   Total needed: {total_tokens_needed:,} tokens")
        print(f"   Model limit: {model_limit:,} tokens")
        
        if total_tokens_needed > model_limit:
            excess_tokens = total_tokens_needed - model_limit
            raise Exception(f"""TOKEN_LIMIT_EXCEEDED: Full CSV content exceeds token limits for model {deployment_name}.

📊 Full Content Token Analysis:
• System prompt: {system_tokens:,} tokens
• Complete CSV data + question: {user_tokens:,} tokens
• Total input tokens: {total_input_tokens:,} tokens
• Reserved for response: {max_response_tokens:,} tokens
• Total tokens needed: {total_tokens_needed:,} tokens
• Model limit: {model_limit:,} tokens
• Excess tokens: {excess_tokens:,} tokens

💡 The complete CSV file is too large for this model.
   Try using a model with higher token limits or split your data into smaller files.""")
        
    except ImportError:
        print("⚠️ tiktoken not available, skipping token validation")
    except Exception as token_error:
        print(f"⚠️ Token counting error: {token_error}")
    
    # Clean endpoint URL
    if not endpoint.endswith('/'):
        endpoint += '/'
    
    url = f"{endpoint}openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"
    
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.3,
        "top_p": 0.95,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
    
    print(f"🚀 Sending complete CSV content to Azure OpenAI...")
    
    response = requests.post(url, headers=headers, json=payload, timeout=120)  # Increased timeout for large content
    
    if response.status_code != 200:
        raise Exception(f"Azure OpenAI API error: {response.status_code} - {response.text}")
    
    result = response.json()
    actual_usage = result.get("usage", {})
    
    print(f"✅ Response received. Actual tokens used: {actual_usage}")
    
    return {
        "answer": result["choices"][0]["message"]["content"],
        "processing_info": {
            "model": deployment_name,
            "provider": "azure_openai",
            "processing_method": "full_content_extraction",
            "data_rows": csv_rows,
            "data_columns": csv_columns,
            "content_length": len(data_summary),
            "actual_tokens_used": actual_usage,
            "full_content_processed": True
        }
    }

def call_openai_api(file_content, filename, question):
    """Call OpenAI API with file content"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY not found in environment variables")
    
    # For OpenAI, we need to decode CSV and send as text
    try:
        csv_text = file_content.decode('utf-8')
    except UnicodeDecodeError:
        raise Exception("Unable to decode CSV file as UTF-8")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that analyzes CSV data and answers questions about it."
            },
            {
                "role": "user",
                "content": f"Here is CSV data from file '{filename}':\n\n{csv_text}\n\nQuestion: {question}\n\nPlease analyze the data and provide a comprehensive answer."
            }
        ],
        "max_tokens": 1500,
        "temperature": 0.7
    }
    
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )
    
    if response.status_code != 200:
        raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
    
    result = response.json()
    return {
        "answer": result["choices"][0]["message"]["content"],
        "processing_info": {
            "model": payload["model"],
            "provider": "openai",
            "tokens_used": result.get("usage", {})
        }
    }

def call_google_api(file_content, filename, question):
    """Call Google Gemini API with file content"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise Exception("GOOGLE_API_KEY not found in environment variables")
    
    # For Google Gemini, decode CSV as text
    try:
        csv_text = file_content.decode('utf-8')
    except UnicodeDecodeError:
        raise Exception("Unable to decode CSV file as UTF-8")
    
    model = os.getenv("GOOGLE_MODEL", "gemini-pro")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Analyze this CSV data from file '{filename}' and answer the question.\n\nCSV Data:\n{csv_text}\n\nQuestion: {question}\n\nProvide a comprehensive analysis and answer."
                    }
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 1500,
            "temperature": 0.7
        }
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    
    if response.status_code != 200:
        raise Exception(f"Google API error: {response.status_code} - {response.text}")
    
    result = response.json()
    return {
        "answer": result["candidates"][0]["content"]["parts"][0]["text"],
        "processing_info": {
            "model": model,
            "provider": "google",
            "tokens_used": result.get("usageMetadata", {})
        }
    }

@app.route('/upload-info', methods=['GET'])
def upload_info():
    """Get information about upload limits and supported formats"""
    provider = determine_llm_provider()
    return jsonify({
        "max_file_size_mb": MAX_FILE_SIZE / (1024 * 1024),
        "supported_formats": ["csv"],
        "description": "Upload CSV files and ask questions about the data",
        "llm_provider": provider,
        "available_providers": list(SUPPORTED_PROVIDERS.keys())
    })
@app.route('/debug-env', methods=['GET'])
def debug_env():
    """Debug endpoint to check environment variables"""
    # Build Azure OpenAI URL for debugging
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    if endpoint and not endpoint.endswith('/'):
        endpoint += '/'
    
    constructed_url = f"{endpoint}openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"
    
    return jsonify({
        "detected_provider": determine_llm_provider(),
        "azure_openai": {
            "api_key_exists": bool(os.getenv("AZURE_OPENAI_API_KEY")),
            "api_key_length": len(os.getenv("AZURE_OPENAI_API_KEY", "")),
            "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            "deployment_name": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            "constructed_url": constructed_url
        },
        "anthropic": {
            "api_key_exists": bool(os.getenv("ANTHROPIC_API_KEY")),
            "api_key_length": len(os.getenv("ANTHROPIC_API_KEY", ""))
        },
        "openai": {
            "api_key_exists": bool(os.getenv("OPENAI_API_KEY")),
            "api_key_length": len(os.getenv("OPENAI_API_KEY", ""))
        },
        "working_directory": os.getcwd()
    })
if __name__ == '__main__':
    # Validate that at least one LLM provider is configured
    provider = determine_llm_provider()
    if not provider:
        print("Error: No LLM provider configured!")
        print("Please set one of the following in your .env file:")
        print("- AZURE_OPENAI_API_KEY for Azure OpenAI GPT-4o (with content extraction)")
        print("- ANTHROPIC_API_KEY for Claude (with direct file upload)")
        print("- OPENAI_API_KEY for GPT")
        print("- GOOGLE_API_KEY for Gemini")
        exit(1)
    
    print(f"Using LLM provider: {provider}")
    app.run(debug=True, host='0.0.0.0', port=5000)