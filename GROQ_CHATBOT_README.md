# 🚀 Kreo-Tech AI Customer Support - Groq-Powered Chatbot

## Overview

This is an advanced AI customer support system powered by Groq's lightning-fast LLM API. The system provides intelligent, context-aware responses based on scraped website data from Kreo-Tech.

## 🌟 Features

### ✨ Groq-Powered Intelligence
- **Lightning Fast**: Sub-second response times using Groq's optimized inference
- **Context-Aware**: Finds relevant information from 1,657 Q&A pairs
- **Smart Matching**: Uses TF-IDF vectorization for accurate context retrieval
- **Professional Responses**: Maintains brand voice and provides comprehensive answers

### 🔧 Two Versions Available

#### 1. Basic Groq Chatbot (`groq_chatbot.py`)
- Simple, clean interface
- Direct API integration
- Essential features for quick deployment

#### 2. Advanced Groq Chatbot (`advanced_groq_chatbot.py`)
- Environment variable configuration
- Comprehensive logging
- Enhanced error handling
- Performance metrics
- Production-ready features

## 📋 Requirements

```bash
pip install groq scikit-learn numpy python-dotenv
```

## 🚀 Quick Start

### Option 1: Use the Launcher
```bash
python run_chatbot.py
```

### Option 2: Run Directly
```bash
# Basic version
python groq_chatbot.py

# Advanced version (requires .env file)
python advanced_groq_chatbot.py
```

### Option 3: Run Tests
```bash
# Test basic chatbot
python test_groq.py

# Test advanced chatbot
python test_advanced_groq.py
```

## ⚙️ Configuration

### Environment Variables (.env file)
```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama3-8b-8192
GROQ_TEMPERATURE=0.3
GROQ_MAX_TOKENS=500
```

### Available Models
- `llama3-8b-8192` (default) - Fast and efficient
- `llama3-70b-8192` - More powerful but slower
- `mixtral-8x7b-32768` - Good balance of speed and quality

## 📊 Performance Metrics

Based on testing with 1,657 Q&A pairs:

| Metric | Value |
|--------|-------|
| **Response Time** | 0.3-0.6 seconds |
| **Context Sources** | Up to 5 relevant matches |
| **Accuracy** | High relevance scoring |
| **Data Coverage** | 500 scraped pages |

## 🎯 Sample Interactions

### Shipping Policy Query
**User**: "What are your shipping policies?"

**AI Response**: Provides comprehensive shipping information including processing times, delay notifications, tracking details, and rate information based on scraped policy data.

### Product Information
**User**: "Tell me about your gaming mice"

**AI Response**: Details about Ikarus, Pegasus, and Hawk gaming mouse series with specifications and features.

### Technical Support
**User**: "How can I contact support?"

**AI Response**: Multiple contact methods including phone, email, online forms, and live chat options.

## 🔍 How It Works

1. **Context Retrieval**: Uses TF-IDF vectorization to find relevant Q&A pairs
2. **Smart Matching**: Calculates cosine similarity for accurate context selection
3. **Prompt Engineering**: Creates comprehensive system prompts with relevant context
4. **Groq Processing**: Leverages Groq's fast LLM inference for intelligent responses
5. **Response Delivery**: Returns contextual, professional customer support answers

## 📁 File Structure

```
website-scraper-ai-support/
├── groq_chatbot.py              # Basic Groq chatbot
├── advanced_groq_chatbot.py     # Advanced version with logging
├── run_chatbot.py               # Launcher script
├── test_groq.py                 # Basic chatbot tests
├── test_advanced_groq.py        # Advanced chatbot tests
├── .env                         # Environment configuration
├── requirements.txt             # Dependencies
└── scraped_data/
    └── kreo-tech/
        └── qa_pairs/
            └── qa_pairs.json    # Training data (1,657 pairs)
```

## 🚨 Error Handling

The system includes comprehensive error handling for:
- API connection issues
- Invalid API keys
- Missing data files
- Vectorization errors
- Response generation failures

## 📈 Advantages Over Previous System

| Feature | Old System | New Groq System |
|---------|------------|-----------------|
| **Response Quality** | Basic similarity matching | AI-powered intelligent responses |
| **Context Understanding** | Limited | Advanced context comprehension |
| **Response Length** | Often truncated | Complete, comprehensive answers |
| **Professional Tone** | Inconsistent | Maintains brand voice |
| **Speed** | Fast (local) | Ultra-fast (0.3-0.6s) |
| **Scalability** | Limited | Highly scalable |

## 🔧 Customization

### Adjusting Response Parameters
```python
# In the chatbot initialization
self.temperature = 0.3  # Lower = more consistent, Higher = more creative
self.max_tokens = 500   # Response length limit
top_k = 5              # Number of context sources
```

### Modifying System Prompts
Edit the `create_system_prompt()` method to customize:
- Brand voice and tone
- Response structure
- Specific instructions
- Context formatting

## 🎉 Success Metrics

✅ **1,657 Q&A pairs** loaded and indexed  
✅ **Sub-second response times** achieved  
✅ **Professional, comprehensive answers** generated  
✅ **Context-aware responses** with relevance scoring  
✅ **Production-ready** with error handling and logging  

## 🚀 Next Steps

1. **Deploy to Production**: Set up on a server with proper API key management
2. **Add Web Interface**: Create a web-based chat interface
3. **Integrate with Website**: Embed as a customer support widget
4. **Monitor Performance**: Track response quality and user satisfaction
5. **Expand Data**: Continue scraping and updating the knowledge base

## 💡 Tips for Best Results

- Use specific questions for better context matching
- The system works best with product, policy, and service inquiries
- Responses improve with more comprehensive scraped data
- Regular data updates maintain accuracy

---

**Powered by Groq's Lightning-Fast LLM Inference** ⚡