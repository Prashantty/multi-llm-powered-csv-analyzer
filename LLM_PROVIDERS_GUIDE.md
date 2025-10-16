# LLM Providers Guide for CSV Analysis

This guide explains the different LLM providers you can use with your CSV Q&A application and their capabilities for file processing.

## 🎯 **Recommended LLM Models for CSV Analysis**

### **1. Anthropic Claude (⭐ BEST CHOICE)**

**Why Claude is Ideal:**
- ✅ **Native File Support**: Can directly process uploaded files without content extraction
- ✅ **Large Context Window**: 200K tokens (handles large CSV files)
- ✅ **Excellent Data Analysis**: Strong analytical and reasoning capabilities
- ✅ **Document Understanding**: Built-in support for CSV, JSON, and other structured data
- ✅ **Safety**: Lower hallucination rates for data analysis

**Supported Models:**
- `claude-3-opus-20240229` - Most capable, best for complex analysis
- `claude-3-sonnet-20240229` - Balanced performance and cost (recommended)
- `claude-3-haiku-20240307` - Fastest and cheapest option

**Setup:**
```bash
# In your .env file
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

**Cost:** ~$3-15 per 1M tokens (depending on model)

---

### **2. OpenAI GPT Models**

**Capabilities:**
- ✅ **Good Data Analysis**: Strong analytical capabilities
- ✅ **Code Generation**: Can generate Python/SQL code for analysis
- ⚠️ **Text-Only**: Requires CSV content to be sent as text
- ⚠️ **Context Limits**: 128K tokens (may truncate large files)

**Supported Models:**
- `gpt-4-turbo-preview` - Best reasoning (recommended)
- `gpt-4` - Reliable but slower
- `gpt-3.5-turbo` - Faster but less capable

**Setup:**
```bash
# In your .env file
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview
```

**Cost:** ~$10-30 per 1M tokens

---

### **3. Google Gemini**

**Capabilities:**
- ✅ **Good Analysis**: Decent analytical capabilities
- ✅ **Fast Processing**: Generally quick responses
- ⚠️ **Text-Only**: Requires CSV content to be sent as text
- ⚠️ **Limited Context**: 32K-1M tokens depending on model

**Supported Models:**
- `gemini-pro` - Standard model (recommended)
- `gemini-pro-vision` - Multimodal but not needed for CSV

**Setup:**
```bash
# In your .env file
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL=gemini-pro
```

**Cost:** ~$0.50-7 per 1M tokens

---

## 🔧 **Alternative LLM Providers for File Processing**

### **Other Models That Support File Analysis:**

#### **1. LlamaParse + Llama Models**
- **Provider**: LlamaIndex
- **File Support**: ✅ Native CSV/Excel support
- **Cost**: Free tier available
- **Setup**: Requires LlamaIndex integration

#### **2. Cohere Command-R+**
- **Provider**: Cohere
- **File Support**: ✅ Document understanding
- **Strength**: Good for RAG applications
- **Cost**: ~$3-15 per 1M tokens

#### **3. Mistral Large**
- **Provider**: Mistral AI
- **File Support**: ⚠️ Text-only but good analysis
- **Strength**: Strong reasoning at lower cost
- **Cost**: ~$2-6 per 1M tokens

#### **4. PaLM 2 (Google)**
- **Provider**: Google Cloud
- **File Support**: ⚠️ Limited
- **Note**: Being deprecated in favor of Gemini

---

## 📊 **Comparison Matrix**

| Provider | File Support | Context Size | Data Analysis | Cost | Speed |
|----------|-------------|--------------|---------------|------|-------|
| **Claude** | ✅ Native | 200K | ⭐⭐⭐⭐⭐ | $$$ | ⭐⭐⭐⭐ |
| **GPT-4** | ⚠️ Text | 128K | ⭐⭐⭐⭐⭐ | $$$$ | ⭐⭐⭐ |
| **Gemini** | ⚠️ Text | 32K-1M | ⭐⭐⭐⭐ | $$ | ⭐⭐⭐⭐⭐ |
| **Cohere** | ✅ Docs | 128K | ⭐⭐⭐⭐ | $$$ | ⭐⭐⭐⭐ |
| **Mistral** | ⚠️ Text | 32K | ⭐⭐⭐⭐ | $$ | ⭐⭐⭐⭐ |

---

## 🚀 **Implementation Details**

### **Current Backend Implementation**

Your updated `app.py` now supports:

1. **File Passthrough**: Receives files without extracting content locally
2. **Multi-Provider Support**: Automatically detects and uses available LLM provider
3. **Direct API Calls**: Makes HTTP requests to LLM APIs
4. **Error Handling**: Comprehensive error handling for each provider

### **File Processing Methods:**

#### **Anthropic (Recommended)**
```python
# Sends file as base64-encoded document
{
    "type": "document",
    "source": {
        "type": "base64",
        "media_type": "text/csv",
        "data": file_base64
    }
}
```

#### **OpenAI & Google**
```python
# Sends CSV content as decoded text
csv_text = file_content.decode('utf-8')
# Includes in message content
```

---

## 💡 **Best Practices**

### **For Large CSV Files:**
1. **Use Claude**: Best context window and file handling
2. **Chunk Processing**: For files >10MB, consider splitting
3. **Preprocessing**: Remove unnecessary columns before upload

### **For Cost Optimization:**
1. **Use Haiku**: For simple queries, Claude Haiku is cheapest
2. **Cache Results**: Implement caching for repeated queries
3. **Optimize Prompts**: Shorter prompts = lower costs

### **For Accuracy:**
1. **Use Opus/GPT-4**: For complex analysis requiring highest accuracy
2. **Validate Results**: Cross-check critical calculations
3. **Iterative Queries**: Break complex questions into simpler parts

---

## 🔑 **Getting API Keys**

### **Anthropic Claude**
1. Visit: https://console.anthropic.com/
2. Sign up and verify your account
3. Go to API Keys section
4. Create a new API key

### **OpenAI**
1. Visit: https://platform.openai.com/
2. Sign up and add payment method
3. Go to API Keys section
4. Create a new secret key

### **Google Gemini**
1. Visit: https://makersuite.google.com/
2. Sign up with Google account
3. Go to "Get API Key"
4. Create and copy the key

---

## 🎯 **Recommendation Summary**

**For Your Use Case (CSV Q&A):**

1. **Primary Choice**: **Anthropic Claude Sonnet**
   - Best file handling
   - Excellent for data analysis
   - Good balance of cost/performance

2. **Backup Option**: **OpenAI GPT-4 Turbo**
   - Excellent analysis capabilities
   - Widely supported
   - Good documentation

3. **Budget Option**: **Google Gemini Pro**
   - Lower cost
   - Good enough for basic analysis
   - Fast processing

Start with Claude Sonnet - it's specifically designed for document analysis and will give you the best results for CSV processing!