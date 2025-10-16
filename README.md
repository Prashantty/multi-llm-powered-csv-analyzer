# Q/A Maker Backend - Flask + Mutli-LLM Support

A simple Flask backend application that processes CSV files and answers questions about the data using Azure OpenAI models.

## Features

- Upload CSV files via REST API
- Ask questions about CSV data
- Powered by Azure OpenAI models
- No chat history storage (stateless)
- CORS enabled for frontend integration
- Comprehensive error handling

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Azure OpenAI

1. Copy the example environment file:
```bash
cp env.example .env
```

2. Edit `.env` with your Azure OpenAI credentials:
```
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-01
```

### 3. Run the Application

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### 1. Health Check
- **GET** `/health`
- Returns server status

### 2. Chat Processing
- **POST** `/chat`
- **Form Data:**
  - `file`: CSV file (max 16MB)
  - `question`: Question about the CSV data
- **Response:**
```json
{
  "success": true,
  "question": "What is the average age?",
  "answer": "Based on the CSV data...",
  "csv_rows": 100,
  "csv_columns": ["name", "age", "city"]
}
```

### 3. Upload Information
- **GET** `/upload-info`
- Returns file upload limits and supported formats

## Usage Example

### Using curl:

```bash
curl -X POST http://localhost:5000/chat \
  -F "file=@data.csv" \
  -F "question=What is the total sales amount?"
```

### Using Python requests:

```python
import requests

url = 'http://localhost:5000/chat'
files = {'file': open('data.csv', 'rb')}
data = {'question': 'What is the average age of customers?'}

response = requests.post(url, files=files, data=data)
print(response.json())
```

## File Constraints

- **Format**: CSV files only
- **Size**: Maximum 16MB
- **Processing**: File content is sent directly to Azure OpenAI

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `400 Bad Request`: Invalid file format, missing parameters
- `500 Internal Server Error`: Azure OpenAI API errors, processing failures

## Security Notes

- Ensure your Azure OpenAI API key is kept secure
- File uploads are temporarily processed in memory
- No persistent storage of uploaded files or chat history
