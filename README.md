# 🤖 AI Customer Support System

An intelligent customer support platform that automatically scrapes your website content and provides AI-powered responses via WhatsApp and Email.

## ✨ Features

- 🕷️ **Automatic Website Scraping** - Extracts content from any website
- 🧠 **AI-Powered Responses** - Uses Groq/OpenAI for intelligent answers
- 📱 **WhatsApp Integration** - Twilio-powered WhatsApp bot
- 📧 **Email Support** - Automated email responses
- 🎯 **Smart Context Matching** - Finds relevant information from your content
- 📊 **Analytics Dashboard** - Track conversations and performance
- 🔧 **Easy Setup** - Environment-based configuration

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Nishant-404/website-scraper-ai-support.git
cd website-scraper-ai-support
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Setup Script
```bash
python setup.py
```

### 4. Configure Environment Variables
Edit the `.env` file and add your API keys:

```env
# Required: Get from https://console.groq.com/
GROQ_API_KEY=gsk_your_groq_api_key_here

# Optional: For WhatsApp integration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token

# Optional: For email integration
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
```

### 5. Run the Application
```bash
python app.py
```

### 6. Open in Browser
Visit `http://localhost:5000` to access the dashboard.

## 📋 Detailed Setup

### API Keys Required

#### 1. Groq API Key (Required)
- Visit [Groq Console](https://console.groq.com/)
- Create an account and generate an API key
- Add to `.env`: `GROQ_API_KEY=gsk_your_key_here`

#### 2. Twilio (For WhatsApp)
- Visit [Twilio Console](https://console.twilio.com/)
- Get Account SID and Auth Token
- Add to `.env`:
  ```env
  TWILIO_ACCOUNT_SID=your_account_sid
  TWILIO_AUTH_TOKEN=your_auth_token
  ```

#### 3. Email SMTP (For Email Support)
For Gmail:
- Enable 2-factor authentication
- Generate an App Password
- Add to `.env`:
  ```env
  SMTP_USERNAME=your-email@gmail.com
  SMTP_PASSWORD=your-app-password
  ```

### Environment Variables

The system uses environment variables for configuration. Key variables include:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GROQ_API_KEY` | Groq API key for AI responses | Yes | - |
| `SECRET_KEY` | Flask secret key | No | Auto-generated |
| `MAX_PAGES_PER_SITE` | Max pages to scrape per website | No | 50 |
| `AI_MODEL` | Groq model to use | No | llama3-8b-8192 |
| `SCRAPING_DELAY` | Delay between requests (seconds) | No | 1 |

See `.env.example` for all available options.

## 🎯 How It Works

### 1. Website Scraping
- Enter your website URL in the dashboard
- System crawls and extracts content
- Content is cleaned and processed
- Q&A pairs are generated automatically

### 2. AI Responses
- Customer messages are analyzed
- Relevant content is found using embeddings
- AI generates contextual responses
- Fallback to human agent if needed

### 3. Multi-Channel Support
- **WhatsApp**: Customers text your WhatsApp number
- **Email**: Customers email your support address
- **Web**: Direct chat on your website

## 📊 Dashboard Features

### Website Management
- Add/update website URLs
- View scraping status
- Manage knowledge base

### Integration Setup
- Configure WhatsApp settings
- Setup email integration
- Test connections

### Analytics
- View conversation history
- Track response accuracy
- Monitor system performance

## 🛠️ Development

### Project Structure
```
website-scraper-ai-support/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── setup.py              # Setup script
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── .env.example         # Environment template
├── scraper/             # Web scraping modules
├── processor/           # Content processing
├── integrations/        # WhatsApp/Email integrations
├── templates/           # HTML templates
├── scraped_data/        # Scraped website data
└── logs/               # Application logs
```

### Running Tests
```bash
# Test website scraping
python test_scraping.py

# Test AI chatbot
python test_redgear_chatbot.py

# Test integrations
python test_integrations.py
```

### Adding New Features

1. **New Integration**: Add to `integrations/` directory
2. **New Processor**: Add to `processor/` directory
3. **New Template**: Add to `templates/` directory

## 🔧 Configuration Options

### AI Model Settings
```env
AI_MODEL=llama3-8b-8192          # Groq model
MAX_TOKENS=1000                  # Response length
TEMPERATURE=0.7                  # Response creativity
SIMILARITY_THRESHOLD=0.7         # Context matching threshold
```

### Scraping Settings
```env
MAX_PAGES_PER_SITE=50           # Pages to scrape
SCRAPING_DELAY=1                # Delay between requests
REQUEST_TIMEOUT=30              # Request timeout
USER_AGENT=Mozilla/5.0...       # Browser user agent
```

### Security Settings
```env
RATE_LIMIT_PER_MINUTE=60        # API rate limiting
JWT_SECRET_KEY=your-jwt-key     # JWT token secret
ENABLE_RATE_LIMITING=True       # Enable rate limiting
```

## 🚨 Troubleshooting

### Common Issues

#### 1. "Configuration error: Missing required environment variables"
- Check your `.env` file exists
- Ensure `GROQ_API_KEY` is set
- Run `python setup.py` to create template

#### 2. "Failed to scrape website"
- Check website URL is accessible
- Verify internet connection
- Some sites block automated scraping

#### 3. "WhatsApp integration not working"
- Verify Twilio credentials
- Check webhook URL is accessible
- Ensure WhatsApp number is verified

#### 4. "AI responses are generic"
- Check if website scraping completed
- Verify Q&A pairs were generated
- Increase `MAX_PAGES_PER_SITE` for more content

### Debug Mode
Enable debug logging:
```env
LOG_LEVEL=DEBUG
FLASK_DEBUG=True
```

## 📈 Scaling for Production

### Database
Switch from SQLite to PostgreSQL:
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
```

### Caching
Enable Redis caching:
```env
REDIS_URL=redis://localhost:6379/0
ENABLE_CACHING=True
```

### Security
- Set strong `SECRET_KEY`
- Enable HTTPS
- Configure rate limiting
- Use environment-specific configs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- 📧 Email: support@yourcompany.com
- 💬 Issues: [GitHub Issues](https://github.com/Nishant-404/website-scraper-ai-support/issues)
- 📚 Documentation: [Wiki](https://github.com/Nishant-404/website-scraper-ai-support/wiki)

## 🎉 Demo

Try the live demo at: [https://your-demo-site.com](https://your-demo-site.com)

Test with these sample questions:
- "What products do you offer?"
- "How can I contact support?"
- "What are your business hours?"

---

Made with ❤️ by [Nishant](https://github.com/Nishant-404)