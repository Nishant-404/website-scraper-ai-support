# AI Customer Support Platform - Project Architecture

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture Principles](#architecture-principles)
3. [Folder Structure](#folder-structure)
4. [Module Documentation](#module-documentation)
5. [Database Schema](#database-schema)
6. [API Documentation](#api-documentation)
7. [Development Guidelines](#development-guidelines)
8. [Deployment Guide](#deployment-guide)

## 🎯 Project Overview

The AI Customer Support Platform is a comprehensive solution that automatically scrapes e-commerce websites to create intelligent customer support chatbots. The platform supports multi-channel deployment (WhatsApp, Email, Web) and provides detailed analytics.

### Key Features
- **Intelligent Web Scraping**: Automatically extract product information from any e-commerce website
- **AI-Powered Chatbot**: Create intelligent customer support bots using scraped product data
- **Multi-Channel Support**: Deploy on WhatsApp, Email, and Web platforms
- **Real-Time Analytics**: Track conversations, performance, and customer satisfaction
- **User Management**: Multi-tenant system with secure user authentication
- **Product Management**: CRUD operations for scraped products with search and filtering

### Technology Stack
- **Backend**: Python Flask with modular architecture
- **Database**: SQLite (development), PostgreSQL (production ready)
- **AI**: Groq API for natural language processing
- **Scraping**: BeautifulSoup, Selenium for web scraping
- **Integrations**: Twilio (WhatsApp), SMTP (Email)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Deployment**: Docker, Nginx ready

## 🏗️ Architecture Principles

### 1. Modular Design
- **Single Responsibility**: Each file contains only one primary function or class
- **Separation of Concerns**: Business logic, routes, and data access are separated
- **Reusability**: Functions are designed to be reusable across the application
- **Testability**: Each module can be tested independently

### 2. Extensive Documentation
- **Minimum 40% comment-to-code ratio** in all files
- **Detailed docstrings** for every function and class
- **Inline comments** explaining complex logic
- **README files** for each major component

### 3. Security First
- **Input validation** on all user inputs
- **Parameterized queries** for database operations
- **Authentication required** for all protected routes
- **Security headers** on all responses
- **Rate limiting** for API endpoints

### 4. Error Handling
- **Comprehensive error handling** in all functions
- **Graceful degradation** when services are unavailable
- **Detailed error logging** for debugging
- **User-friendly error messages**

## 📁 Folder Structure

```
website-scraper-ai-support/
├── 📁 functions/                    # Core business logic functions
│   ├── 📁 user/                     # User management functions
│   │   ├── create_user.py           # User registration logic
│   │   ├── authenticate_user.py     # User authentication logic
│   │   └── update_user.py           # User profile updates
│   ├── 📁 product/                  # Product management functions
│   │   ├── add_product.py           # Product creation logic
│   │   ├── get_products.py          # Product retrieval logic
│   │   ├── update_product.py        # Product update logic
│   │   └── delete_product.py        # Product deletion logic
│   ├── 📁 chat/                     # Chat and AI functions
│   │   ├── process_message.py       # Message processing logic
│   │   ├── generate_response.py     # AI response generation
│   │   └── context_manager.py       # Conversation context management
│   └── 📁 auth/                     # Authentication utilities
│       ├── session_manager.py       # Session management
│       └── permissions.py           # Permission checking
├── 📁 routes/                       # Flask route handlers
│   ├── auth_routes.py               # Authentication routes
│   ├── product_routes.py            # Product management routes
│   ├── api_routes.py                # API endpoints
│   └── main_routes.py               # General application routes
├── 📁 database/                     # Database operations
│   ├── 📁 models/                   # Database models
│   │   ├── user_model.py            # User data model
│   │   ├── product_model.py         # Product data model
│   │   └── conversation_model.py    # Conversation data model
│   ├── 📁 operations/               # Database operations
│   │   ├── user_operations.py       # User CRUD operations
│   │   ├── product_operations.py    # Product CRUD operations
│   │   └── analytics_operations.py  # Analytics queries
│   └── 📁 migrations/               # Database migrations
│       └── initial_schema.sql       # Initial database schema
├── 📁 scraper/                      # Web scraping functionality
│   ├── website_crawler.py           # Website crawling logic
│   ├── product_extractor.py         # Product data extraction
│   ├── data_cleaner.py              # Data cleaning and validation
│   └── scraper_config.py            # Scraping configuration
├── 📁 ai/                           # AI and chatbot functionality
│   ├── 📁 chatbot/                  # Chatbot engine
│   │   ├── chatbot_engine.py        # Main chatbot logic
│   │   ├── intent_classifier.py     # Intent classification
│   │   └── entity_extractor.py      # Entity extraction
│   ├── 📁 response/                 # Response generation
│   │   ├── response_generator.py    # Response generation logic
│   │   ├── template_manager.py      # Response templates
│   │   └── personalization.py       # Response personalization
│   └── 📁 training/                 # AI training utilities
│       ├── data_processor.py        # Training data processing
│       └── model_trainer.py         # Model training logic
├── 📁 integrations/                 # Third-party integrations
│   ├── 📁 whatsapp/                 # WhatsApp integration
│   │   ├── whatsapp_client.py       # WhatsApp API client
│   │   ├── message_handler.py       # Message handling
│   │   └── webhook_handler.py       # Webhook processing
│   ├── 📁 email/                    # Email integration
│   │   ├── email_client.py          # Email API client
│   │   ├── email_parser.py          # Email parsing
│   │   └── email_sender.py          # Email sending
│   └── 📁 webhook/                  # Webhook management
│       ├── webhook_server.py        # Webhook server
│       └── webhook_validator.py     # Webhook validation
├── 📁 utils/                        # Utility functions
│   ├── validators.py                # Input validation utilities
│   ├── helpers.py                   # General helper functions
│   ├── constants.py                 # Application constants
│   ├── formatters.py                # Data formatting utilities
│   └── security.py                  # Security utilities
├── 📁 config/                       # Configuration files
│   ├── development.py               # Development configuration
│   ├── production.py                # Production configuration
│   ├── testing.py                   # Testing configuration
│   └── base_config.py               # Base configuration
├── 📁 templates/                    # HTML templates
│   ├── base.html                    # Base template
│   ├── home.html                    # Landing page
│   ├── dashboard.html               # User dashboard
│   ├── products.html                # Products management
│   ├── login.html                   # Login page
│   ├── signup.html                  # Registration page
│   └── error.html                   # Error pages
├── 📁 static/                       # Static assets
│   ├── 📁 css/                      # Stylesheets
│   ├── 📁 js/                       # JavaScript files
│   └── 📁 images/                   # Images and icons
├── 📁 tests/                        # Test files
│   ├── 📁 unit/                     # Unit tests
│   ├── 📁 integration/              # Integration tests
│   └── 📁 e2e/                      # End-to-end tests
├── 📁 docs/                         # Documentation
│   ├── PROJECT_ARCHITECTURE.md     # This file
│   ├── API_DOCUMENTATION.md        # API documentation
│   ├── DEPLOYMENT_GUIDE.md         # Deployment instructions
│   └── USER_MANUAL.md              # User manual
├── main_app.py                      # Main application entry point
├── database.py                      # Database connection and models
├── config.py                        # Configuration management
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables example
├── .env                            # Environment variables (not in git)
├── PROJECT_GROUND_RULES.txt        # Development ground rules
└── README.md                       # Project README
```

## 📚 Module Documentation

### Core Functions (`functions/`)

#### User Management (`functions/user/`)
- **create_user.py**: Handles user registration with validation and security
- **authenticate_user.py**: Manages user login and session validation
- **update_user.py**: Handles user profile updates and settings

#### Product Management (`functions/product/`)
- **add_product.py**: Creates new products with validation and JSON handling
- **get_products.py**: Retrieves products with filtering and pagination
- **update_product.py**: Updates existing product information
- **delete_product.py**: Handles product deletion (soft delete)

#### Chat and AI (`functions/chat/`)
- **process_message.py**: Processes incoming chat messages
- **generate_response.py**: Generates AI responses using Groq API
- **context_manager.py**: Manages conversation context and history

### Route Handlers (`routes/`)

#### Authentication Routes (`routes/auth_routes.py`)
- `/login` - User authentication
- `/signup` - User registration
- `/logout` - User logout
- Authentication decorators and utilities

#### Product Routes (`routes/product_routes.py`)
- `/products` - Product management page
- `/api/products/<id>` - Product CRUD API
- `/api/products/search` - Product search API
- `/api/products/categories` - Category management

### Database Layer (`database.py`)
- **Database Class**: Main database connection and operations
- **User Model**: User data structure and validation
- **Product Model**: Product data structure and JSON handling
- **Conversation Model**: Chat conversation management

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    company_name TEXT NOT NULL,
    website_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

### Products Table
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    price TEXT,
    category TEXT,
    url TEXT,
    image_url TEXT,
    features TEXT,  -- JSON
    specifications TEXT,  -- JSON
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### QA Pairs Table
```sql
CREATE TABLE qa_pairs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category TEXT,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### Conversations Table
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    customer_phone TEXT,
    customer_email TEXT,
    message TEXT NOT NULL,
    response TEXT,
    channel TEXT,  -- whatsapp, email, web
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## 🔌 API Documentation

### Authentication Endpoints

#### POST /login
Authenticate user and create session.

**Request Body:**
```json
{
    "username": "user@example.com",
    "password": "password123"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "user@example.com",
        "company_name": "Acme Corp"
    }
}
```

#### POST /signup
Register new user account.

**Request Body:**
```json
{
    "username": "newuser",
    "email": "user@example.com",
    "password": "password123",
    "company_name": "Acme Corp",
    "website_url": "https://acme.com"
}
```

### Product Endpoints

#### GET /api/products
Get user's products with filtering and pagination.

**Query Parameters:**
- `category` (string): Filter by category
- `search` (string): Search in name/description
- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20)

**Response:**
```json
{
    "success": true,
    "products": [...],
    "pagination": {
        "total_count": 100,
        "page_count": 5,
        "current_page": 1,
        "has_next": true,
        "has_previous": false
    }
}
```

#### GET /api/products/{id}
Get specific product by ID.

**Response:**
```json
{
    "id": 1,
    "name": "Product Name",
    "description": "Product description",
    "price": "$99.99",
    "category": "Electronics",
    "features": {"color": "red"},
    "specifications": {"weight": "1kg"}
}
```

#### PUT /api/products/{id}
Update product information.

**Request Body:**
```json
{
    "name": "Updated Product Name",
    "description": "Updated description",
    "price": "$199.99"
}
```

#### DELETE /api/products/{id}
Delete product (soft delete).

**Response:**
```json
{
    "success": true,
    "message": "Product deleted successfully"
}
```

## 🛠️ Development Guidelines

### Code Quality Standards
1. **Function Size**: Maximum 50 lines per function
2. **File Size**: Maximum 200 lines per file
3. **Comments**: Minimum 40% comment-to-code ratio
4. **Documentation**: Every function must have detailed docstring
5. **Error Handling**: Every function must handle errors gracefully

### Naming Conventions
- **Files**: snake_case.py (e.g., `user_authentication.py`)
- **Functions**: snake_case (e.g., `create_user_account`)
- **Classes**: PascalCase (e.g., `UserManager`)
- **Variables**: snake_case (e.g., `user_id`)
- **Constants**: UPPER_CASE (e.g., `MAX_PRODUCTS`)

### Testing Requirements
- **Unit Tests**: Every function must have unit tests
- **Integration Tests**: Every route must have integration tests
- **Test Coverage**: Minimum 80% code coverage
- **Test Documentation**: Tests must be well documented

### Security Requirements
- **Input Validation**: All user inputs must be validated
- **SQL Injection Prevention**: Use parameterized queries
- **Authentication**: All protected routes require authentication
- **Rate Limiting**: API endpoints must have rate limiting
- **Security Headers**: All responses include security headers

## 🚀 Deployment Guide

### Development Environment
1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd website-scraper-ai-support
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize Database**
   ```bash
   python -c "from database import Database; Database()"
   ```

5. **Run Application**
   ```bash
   python main_app.py
   ```

### Production Deployment
1. **Docker Deployment**
   ```bash
   docker build -t ai-support-platform .
   docker run -p 80:5000 ai-support-platform
   ```

2. **Environment Variables**
   - `FLASK_ENV=production`
   - `SECRET_KEY=<secure-secret-key>`
   - `DATABASE_URL=<production-database-url>`
   - `GROQ_API_KEY=<your-groq-api-key>`

3. **Database Migration**
   ```bash
   python database/migrations/migrate.py
   ```

4. **Nginx Configuration**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Monitoring and Logging
- **Application Logs**: Stored in `app.log`
- **Error Tracking**: Integrated with logging system
- **Performance Monitoring**: Response time headers
- **Health Checks**: `/health` endpoint for monitoring

## 📈 Performance Considerations

### Database Optimization
- **Indexing**: Proper indexes on frequently queried columns
- **Query Optimization**: Efficient queries with proper joins
- **Connection Pooling**: Database connection pooling for scalability
- **Caching**: Redis caching for frequently accessed data

### Application Performance
- **Lazy Loading**: Load data only when needed
- **Pagination**: Paginate large datasets
- **Async Processing**: Use background tasks for heavy operations
- **CDN**: Use CDN for static assets

### Scalability
- **Horizontal Scaling**: Design for multiple server instances
- **Load Balancing**: Distribute traffic across servers
- **Microservices**: Consider microservices for large scale
- **Caching Strategy**: Implement comprehensive caching

## 🔒 Security Measures

### Authentication & Authorization
- **Password Hashing**: SHA-256 password hashing
- **Session Management**: Secure session handling
- **Rate Limiting**: Prevent brute force attacks
- **Permission Checks**: Role-based access control

### Data Protection
- **Input Sanitization**: Clean all user inputs
- **SQL Injection Prevention**: Parameterized queries
- **XSS Prevention**: Output encoding and CSP headers
- **CSRF Protection**: CSRF tokens for forms

### Infrastructure Security
- **HTTPS**: SSL/TLS encryption for all traffic
- **Security Headers**: Comprehensive security headers
- **Firewall**: Network-level security
- **Regular Updates**: Keep dependencies updated

## 📊 Monitoring & Analytics

### Application Metrics
- **Response Times**: Track API response times
- **Error Rates**: Monitor error frequencies
- **User Activity**: Track user engagement
- **System Resources**: Monitor CPU, memory, disk usage

### Business Metrics
- **User Registration**: Track new user signups
- **Product Scraping**: Monitor scraping success rates
- **Conversation Volume**: Track chat interactions
- **User Satisfaction**: Monitor user feedback

### Alerting
- **Error Alerts**: Immediate notification for critical errors
- **Performance Alerts**: Alerts for performance degradation
- **Security Alerts**: Notifications for security events
- **Business Alerts**: Alerts for business metric thresholds

---

This architecture document serves as the comprehensive guide for understanding, developing, and maintaining the AI Customer Support Platform. It should be updated as the system evolves and new features are added.