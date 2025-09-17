# 🤖 AI Customer Support Platform

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/Code%20Style-Modular-purple.svg)](PROJECT_GROUND_RULES.txt)

> **Transform any e-commerce website into an intelligent customer support system with AI-powered chatbots, multi-channel deployment, and comprehensive analytics.**

## 🌟 Features

### 🔍 Intelligent Web Scraping
- **Automated Product Extraction**: Scrape product information from any e-commerce website
- **Smart Data Cleaning**: Advanced content processing and validation
- **Real-time Updates**: Keep product catalogs synchronized with source websites
- **Multi-format Support**: Handle various website structures and formats

### 🤖 AI-Powered Chatbot
- **Natural Language Processing**: Powered by Groq API for intelligent responses
- **Context-Aware Conversations**: Maintain conversation history and context
- **Product-Specific Responses**: Generate answers based on scraped product data
- **Customizable Personality**: Adapt chatbot tone and style to your brand

### 📱 Multi-Channel Deployment
- **WhatsApp Integration**: Deploy chatbots on WhatsApp Business API
- **Email Support**: Handle customer inquiries via email
- **Web Chat Widget**: Embed chat functionality on your website
- **Unified Dashboard**: Manage all channels from a single interface

### 📊 Comprehensive Analytics
- **Conversation Tracking**: Monitor all customer interactions
- **Performance Metrics**: Track response times and satisfaction rates
- **Usage Analytics**: Understand customer behavior and preferences
- **Export Capabilities**: Download data for further analysis

### 👥 Multi-Tenant Architecture
- **User Management**: Secure user registration and authentication
- **Isolated Data**: Each user's data is completely separate
- **Role-Based Access**: Different permission levels for team members
- **Scalable Design**: Support thousands of concurrent users

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/ai-customer-support-platform.git
   cd ai-customer-support-platform
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your configuration:
   ```env
   SECRET_KEY=your-secret-key-here
   GROQ_API_KEY=your-groq-api-key
   DEBUG=True
   LOG_LEVEL=INFO
   ```

5. **Initialize Database**
   ```bash
   python -c "from database import Database; Database()"
   ```

6. **Run the Application**
   ```bash
   python main_app.py
   ```

7. **Access the Platform**
   Open your browser and navigate to `http://localhost:5000`

## 📖 Usage Guide

### 1. User Registration
1. Navigate to `/signup`
2. Fill in your details:
   - Username
   - Email address
   - Password
   - Company name
   - Website URL to scrape

### 2. Website Setup
1. Log in to your dashboard
2. Go to "Website Setup"
3. Enter your e-commerce website URL
4. Click "Start Scraping" to extract products

### 3. Product Management
1. Visit the "Products" page
2. View all scraped products
3. Edit product information if needed
4. Use filters to find specific products

### 4. Chatbot Testing
1. Go to the dashboard
2. Use the "Test Chatbot" feature
3. Ask questions about your products
4. See AI-generated responses

### 5. Analytics Dashboard
1. Navigate to "Analytics"
2. View conversation metrics
3. Monitor performance statistics
4. Export data for analysis

## 🏗️ Architecture

### Modular Design
The platform follows a **strict modular architecture** with these principles:

- **Single Responsibility**: Each file contains only one primary function
- **Extensive Documentation**: Minimum 40% comment-to-code ratio
- **Separation of Concerns**: Business logic, routes, and data access are separated
- **Comprehensive Testing**: Every function has unit tests

### Project Structure
```
website-scraper-ai-support/
├── 📁 functions/           # Core business logic
│   ├── user/              # User management functions
│   ├── product/           # Product management functions
│   └── chat/              # Chat and AI functions
├── 📁 routes/             # Flask route handlers
├── 📁 database/           # Database operations
├── 📁 scraper/            # Web scraping functionality
├── 📁 ai/                 # AI and chatbot functionality
├── 📁 integrations/       # Third-party integrations
├── 📁 utils/              # Utility functions
├── 📁 templates/          # HTML templates
├── 📁 static/             # CSS, JS, images
├── 📁 tests/              # Test files
├── 📁 docs/               # Documentation
└── main_app.py            # Application entry point
```

## 🔧 Configuration

### Environment Variables
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Flask secret key for sessions | Yes | - |
| `GROQ_API_KEY` | Groq API key for AI responses | Yes | - |
| `DEBUG` | Enable debug mode | No | `False` |
| `LOG_LEVEL` | Logging level | No | `INFO` |
| `DATABASE_URL` | Database connection URL | No | `sqlite:///app.db` |
| `MAX_CONTENT_LENGTH` | Max upload size | No | `16MB` |

### Database Configuration
The platform uses SQLite by default for development. For production, configure PostgreSQL:

```env
DATABASE_URL=postgresql://username:password@localhost/dbname
```

### AI Configuration
Get your Groq API key from [Groq Console](https://console.groq.com):

```env
GROQ_API_KEY=gsk_your_api_key_here
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=.

# Run specific test file
python -m pytest tests/unit/test_user_functions.py
```

### Test Structure
- **Unit Tests**: Test individual functions in isolation
- **Integration Tests**: Test route handlers and database operations
- **End-to-End Tests**: Test complete user workflows

### Writing Tests
Every function must have corresponding tests:

```python
def test_create_user():
    """Test user creation functionality."""
    result = create_new_user(
        username="testuser",
        email="test@example.com",
        password="TestPass123",
        company_name="Test Company",
        website_url="https://test.com"
    )
    assert result['success'] == True
    assert result['user_id'] is not None
```

## 🔌 API Documentation

### Authentication Endpoints

#### POST /login
Authenticate user and create session.

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "password123"
  }'
```

#### POST /signup
Register new user account.

```bash
curl -X POST http://localhost:5000/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "password123",
    "company_name": "Acme Corp",
    "website_url": "https://acme.com"
  }'
```

### Product Endpoints

#### GET /api/products
Get user's products with filtering.

```bash
curl -X GET "http://localhost:5000/api/products?category=Electronics&search=iPhone&page=1&limit=10" \
  -H "Cookie: session=your-session-cookie"
```

#### GET /api/products/{id}
Get specific product by ID.

```bash
curl -X GET http://localhost:5000/api/products/123 \
  -H "Cookie: session=your-session-cookie"
```

#### PUT /api/products/{id}
Update product information.

```bash
curl -X PUT http://localhost:5000/api/products/123 \
  -H "Content-Type: application/json" \
  -H "Cookie: session=your-session-cookie" \
  -d '{
    "name": "Updated Product Name",
    "price": "$199.99"
  }'
```

#### DELETE /api/products/{id}
Delete product (soft delete).

```bash
curl -X DELETE http://localhost:5000/api/products/123 \
  -H "Cookie: session=your-session-cookie"
```

## 🚀 Deployment

### Development Deployment
```bash
python main_app.py
```

### Production Deployment with Docker
1. **Build Docker Image**
   ```bash
   docker build -t ai-support-platform .
   ```

2. **Run Container**
   ```bash
   docker run -d \
     -p 80:5000 \
     -e SECRET_KEY=your-secret-key \
     -e GROQ_API_KEY=your-groq-key \
     -e FLASK_ENV=production \
     ai-support-platform
   ```

### Production Deployment with Nginx
1. **Install Nginx**
   ```bash
   sudo apt install nginx
   ```

2. **Configure Nginx**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **Enable SSL with Let's Encrypt**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

## 🛠️ Development

### Code Quality Standards
- **Function Size**: Maximum 50 lines per function
- **File Size**: Maximum 200 lines per file
- **Comments**: Minimum 40% comment-to-code ratio
- **Documentation**: Every function must have detailed docstring
- **Error Handling**: Every function must handle errors gracefully

### Adding New Features
1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature-name
   ```

2. **Follow Modular Architecture**
   - Create function in appropriate `functions/` subdirectory
   - Add route handler in appropriate `routes/` file
   - Write comprehensive tests
   - Update documentation

3. **Code Review Checklist**
   - [ ] Function has detailed docstring
   - [ ] Comprehensive error handling
   - [ ] Unit tests written and passing
   - [ ] Code follows naming conventions
   - [ ] Comments explain complex logic
   - [ ] Security considerations addressed

### Contributing Guidelines
1. **Fork the Repository**
2. **Create Feature Branch**
3. **Follow Code Standards**
4. **Write Tests**
5. **Update Documentation**
6. **Submit Pull Request**

## 📚 Documentation

### Available Documentation
- **[Project Ground Rules](PROJECT_GROUND_RULES.txt)**: Development principles and standards
- **[Architecture Guide](docs/PROJECT_ARCHITECTURE.md)**: Detailed system architecture
- **[API Documentation](docs/API_DOCUMENTATION.md)**: Complete API reference
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)**: Production deployment instructions
- **[User Manual](docs/USER_MANUAL.md)**: End-user documentation

### Generating Documentation
```bash
# Generate API documentation
python scripts/generate_api_docs.py

# Generate code documentation
python scripts/generate_code_docs.py
```

## 🔒 Security

### Security Features
- **Password Hashing**: SHA-256 password hashing
- **Session Management**: Secure session handling with Flask-Session
- **Rate Limiting**: Prevent brute force attacks
- **Input Validation**: Comprehensive input sanitization
- **SQL Injection Prevention**: Parameterized database queries
- **XSS Prevention**: Output encoding and CSP headers
- **CSRF Protection**: CSRF tokens for all forms

### Security Best Practices
- Keep dependencies updated
- Use HTTPS in production
- Implement proper logging and monitoring
- Regular security audits
- Follow OWASP guidelines

## 📊 Performance

### Performance Features
- **Database Optimization**: Proper indexing and query optimization
- **Caching**: Redis caching for frequently accessed data
- **Pagination**: Efficient handling of large datasets
- **Lazy Loading**: Load data only when needed
- **Connection Pooling**: Database connection pooling

### Performance Monitoring
- Response time tracking
- Error rate monitoring
- Resource usage monitoring
- User activity analytics

## 🤝 Support

### Getting Help
- **Documentation**: Check the comprehensive documentation
- **Issues**: Create an issue on GitHub
- **Discussions**: Join community discussions
- **Email**: Contact support@example.com

### Common Issues
1. **Database Connection Errors**
   - Check database configuration
   - Ensure database server is running
   - Verify connection credentials

2. **API Key Issues**
   - Verify Groq API key is correct
   - Check API key permissions
   - Ensure sufficient API credits

3. **Scraping Issues**
   - Check website accessibility
   - Verify website structure hasn't changed
   - Review scraping logs for errors

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Groq**: For providing the AI API
- **Flask**: For the excellent web framework
- **BeautifulSoup**: For web scraping capabilities
- **Bootstrap**: For responsive UI components
- **Contributors**: All the developers who contributed to this project

## 📈 Roadmap

### Version 1.1 (Next Release)
- [ ] Advanced scraping algorithms
- [ ] Machine learning model training
- [ ] Enhanced analytics dashboard
- [ ] Mobile app support

### Version 1.2 (Future)
- [ ] Multi-language support
- [ ] Advanced AI features
- [ ] Enterprise integrations
- [ ] Advanced security features

### Version 2.0 (Long-term)
- [ ] Microservices architecture
- [ ] Kubernetes deployment
- [ ] Advanced machine learning
- [ ] Real-time collaboration

---

## 🚀 Get Started Today!

Ready to transform your customer support? Follow the [Quick Start](#-quick-start) guide and have your AI-powered customer support system running in minutes!

For detailed information, check out our [comprehensive documentation](docs/) or [contact our support team](mailto:support@example.com).

**Happy coding! 🎉**