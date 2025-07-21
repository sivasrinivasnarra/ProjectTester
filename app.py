"""
AI-Powered Development Assistant - Main Streamlit Application
"""

import streamlit as st
import os
import json
import zipfile
from datetime import datetime
import tempfile
import base64
from pathlib import Path

# Import core modules
from core import AIEngine, CodeGenerator, TestGenerator, ErrorHandler, DeployChecker
from utils.file_manager import FileManager
from utils.code_analyzer import CodeAnalyzer
from utils.templates import TemplateManager

# Page configuration
st.set_page_config(
    page_title="AI-Powered Development Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .upload-area {
        border: 2px dashed #ccc;
        border-radius: 0.5rem;
        padding: 2rem;
        text-align: center;
        background-color: #fafafa;
    }
    .tech-stack-card {
        background-color: #e3f2fd;
        border: 1px solid #bbdefb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    body {
        background-color: #f8f9fa;
        font-family: "Segoe UI", sans-serif;
    }
    .stButton>button {
        border-radius: 4px;
        padding: 0.5rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_files' not in st.session_state:
    st.session_state.generated_files = []
if 'current_requirement' not in st.session_state:
    st.session_state.current_requirement = ""
if 'tech_stack' not in st.session_state:
    st.session_state.tech_stack = None
if 'uploaded_document' not in st.session_state:
    st.session_state.uploaded_document = None
if 'uploaded_project_path' not in st.session_state:
    st.session_state.uploaded_project_path = None
if 'uploaded_project_files' not in st.session_state:
    st.session_state.uploaded_project_files = []

# Initialize core components
@st.cache_resource
def initialize_components():
    return {
        'ai_engine': AIEngine(),
        'code_generator': CodeGenerator(),
        'test_generator': TestGenerator(),
        'error_handler': ErrorHandler(),
        'deploy_checker': DeployChecker(),
        'file_manager': FileManager(),
        'code_analyzer': CodeAnalyzer(),
        'template_manager': TemplateManager()
    }

components = initialize_components()

# Helper to log errors and display them
def handle_and_display_error(error: Exception, context: str):
    """Record error via ErrorHandler and display to user."""
    components['error_handler'].handle_error(error, context)
    st.error(f"{context}: {str(error)}")

# Document processing functions
def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except ImportError as e:
        handle_and_display_error(e, "extract_text_from_pdf: missing PyPDF2")
        return None
    except Exception as e:
        handle_and_display_error(e, "extract_text_from_pdf")
        return None

def extract_text_from_docx(docx_file):
    """Extract text from Word document"""
    try:
        import docx
        doc = docx.Document(docx_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except ImportError as e:
        handle_and_display_error(e, "extract_text_from_docx: missing python-docx")
        return None
    except Exception as e:
        handle_and_display_error(e, "extract_text_from_docx")
        return None

def extract_text_from_txt(txt_file):
    """Extract text from text file"""
    try:
        return txt_file.read().decode('utf-8')
    except Exception as e:
        handle_and_display_error(e, "extract_text_from_txt")
        return None

def process_uploaded_document(uploaded_file):
    """Process uploaded document and extract text"""
    if uploaded_file is None:
        return None
    
    file_extension = uploaded_file.name.lower().split('.')[-1]
    
    if file_extension == 'pdf':
        return extract_text_from_pdf(uploaded_file)
    elif file_extension in ['docx', 'doc']:
        return extract_text_from_docx(uploaded_file)
    elif file_extension == 'txt':
        return extract_text_from_txt(uploaded_file)
    else:
        handle_and_display_error(ValueError("Unsupported file"), f"process_uploaded_document: {file_extension}")
        return None

# Helper functions for uploaded projects
def extract_project_zip(uploaded_zip) -> str | None:
    """Extract uploaded project ZIP to a temporary directory."""
    try:
        temp_dir = tempfile.mkdtemp(prefix="uploaded_project_")
        with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        return temp_dir
    except Exception as e:
        handle_and_display_error(e, "extract_project_zip")
        return None

def list_python_files(project_dir: str) -> list[str]:
    """List Python files inside the extracted project."""
    py_files = []
    for root, _, files in os.walk(project_dir):
        for f in files:
            if f.endswith('.py'):
                py_files.append(os.path.join(root, f))
    return py_files

def suggest_tech_stack(requirement_text, ai_engine, model="gpt-4o-mini"):
    """Suggest appropriate tech stack based on requirements"""
    try:
        prompt = f"""
        You are a technical architect. Analyze the following requirement and suggest exactly 3 different technology stack options.

        Requirement: {requirement_text}

        For each tech stack option, provide:
        1. Programming Language (with version)
        2. Framework(s)
        3. Database (if needed)
        4. Additional libraries/dependencies
        5. Development tools
        6. Deployment considerations
        7. Pros and cons
        8. Complexity level (Beginner/Intermediate/Advanced)
        9. Estimated development time
        10. Best use case

        IMPORTANT: Respond with ONLY a valid JSON array. No additional text, no explanations, no markdown formatting.

        [
            {{
                "id": 1,
                "name": "Tech Stack Name",
                "language": "Programming Language",
                "framework": "Main Framework",
                "database": "Database Type",
                "dependencies": ["list", "of", "dependencies"],
                "tools": ["development", "tools"],
                "deployment": "Deployment method",
                "pros": ["pro1", "pro2", "pro3"],
                "cons": ["con1", "con2"],
                "complexity": "Beginner/Intermediate/Advanced",
                "estimated_time": "time estimate",
                "best_use_case": "When to use this stack"
            }},
            {{
                "id": 2,
                "name": "Tech Stack Name 2",
                "language": "Programming Language 2",
                "framework": "Main Framework 2",
                "database": "Database Type 2",
                "dependencies": ["list", "of", "dependencies"],
                "tools": ["development", "tools"],
                "deployment": "Deployment method",
                "pros": ["pro1", "pro2", "pro3"],
                "cons": ["con1", "con2"],
                "complexity": "Beginner/Intermediate/Advanced",
                "estimated_time": "time estimate",
                "best_use_case": "When to use this stack"
            }},
            {{
                "id": 3,
                "name": "Tech Stack Name 3",
                "language": "Programming Language 3",
                "framework": "Main Framework 3",
                "database": "Database Type 3",
                "dependencies": ["list", "of", "dependencies"],
                "tools": ["development", "tools"],
                "deployment": "Deployment method",
                "pros": ["pro1", "pro2", "pro3"],
                "cons": ["con1", "con2"],
                "complexity": "Beginner/Intermediate/Advanced",
                "estimated_time": "time estimate",
                "best_use_case": "When to use this stack"
            }}
        ]
        """
        
        response = ai_engine.generate_response(prompt, model=model)
        
        # Try to parse JSON from response
        try:
            import json
            import re
            
            # Clean the response - remove any markdown formatting
            cleaned_response = response.strip()
            
            # Remove markdown code blocks if present
            cleaned_response = re.sub(r'```json\s*', '', cleaned_response)
            cleaned_response = re.sub(r'```\s*$', '', cleaned_response)
            
            # Find JSON array
            start_idx = cleaned_response.find('[')
            end_idx = cleaned_response.rfind(']') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = cleaned_response[start_idx:end_idx]
                result = json.loads(json_str)
                
                # Validate the structure
                if isinstance(result, list) and len(result) > 0:
                    return result
                else:
                    st.error("Invalid tech stack response structure")
                    return _get_fallback_tech_stacks()
            else:
                # Try parsing the entire response as JSON
                result = json.loads(cleaned_response)
                if isinstance(result, list) and len(result) > 0:
                    return result
                else:
                    st.error("Response is not a valid JSON array")
                    return _get_fallback_tech_stacks()
                    
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse tech stack response as JSON: {str(e)}")
            st.error("Raw response preview:")
            st.code(response[:500] + "..." if len(response) > 500 else response)
            st.info("Using fallback tech stack suggestions...")
            return _get_fallback_tech_stacks()
            
    except Exception as e:
        handle_and_display_error(e, "suggest_tech_stack")
        return _get_fallback_tech_stacks()

def _get_fallback_tech_stacks():
    """Provide fallback tech stack suggestions when AI fails"""
    return [
        {
            "id": 1,
            "name": "Python Django Stack",
            "language": "Python 3.11",
            "framework": "Django 4.2",
            "database": "PostgreSQL",
            "dependencies": ["django", "psycopg2", "djangorestframework", "celery"],
            "tools": ["pip", "virtualenv", "git", "docker"],
            "deployment": "Docker + AWS",
            "pros": ["Rapid development", "Built-in admin", "Large ecosystem", "Mature framework"],
            "cons": ["Monolithic", "Learning curve", "Less flexible"],
            "complexity": "Intermediate",
            "estimated_time": "4-6 weeks",
            "best_use_case": "Web applications with complex business logic"
        },
        {
            "id": 2,
            "name": "React Node.js Stack",
            "language": "JavaScript/TypeScript",
            "framework": "React 18 + Node.js",
            "database": "MongoDB",
            "dependencies": ["react", "express", "mongoose", "socket.io"],
            "tools": ["npm", "webpack", "eslint", "jest"],
            "deployment": "Vercel + MongoDB Atlas",
            "pros": ["Fast development", "Rich ecosystem", "Scalable", "Real-time capable"],
            "cons": ["Complex setup", "Many dependencies", "JavaScript fatigue"],
            "complexity": "Advanced",
            "estimated_time": "6-8 weeks",
            "best_use_case": "Modern web applications with real-time features"
        },
        {
            "id": 3,
            "name": "Python FastAPI Stack",
            "language": "Python 3.11",
            "framework": "FastAPI",
            "database": "SQLite/PostgreSQL",
            "dependencies": ["fastapi", "uvicorn", "sqlalchemy", "pydantic"],
            "tools": ["pip", "poetry", "git", "docker"],
            "deployment": "Docker + Cloud Run",
            "pros": ["Fast performance", "Auto documentation", "Type hints", "Modern"],
            "cons": ["Newer ecosystem", "Less mature", "Smaller community"],
            "complexity": "Intermediate",
            "estimated_time": "3-5 weeks",
            "best_use_case": "API-first applications and microservices"
        }
    ]

def _get_fallback_code(tech_stack_name, requirement):
    """Generate fallback code templates when AI is not available"""
    
    if "Django" in tech_stack_name:
        return {
            "main_code": {
                "success": True,
                "files": {
                    "main.py": f'''"""
{requirement}

Django Application Template
"""

import os
import django
from django.core.wsgi import get_wsgi_application

# Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# WSGI application
application = get_wsgi_application()

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
''',
                    "config.py": '''"""
Configuration settings for Django application
"""

import os
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'your-secret-key-here'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
''',
                    "utils.py": '''"""
Utility functions for the application
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def validate_input(data: Dict[str, Any]) -> bool:
    """Validate input data"""
    if not isinstance(data, dict):
        return False
    return True

def format_response(data: Any) -> Dict[str, Any]:
    """Format response data"""
    return {
        "success": True,
        "data": data,
        "timestamp": "2024-01-01T00:00:00Z"
    }
''',
                    "models.py": '''"""
Database models for Django application
"""

from django.db import models
from django.contrib.auth.models import User

class BaseModel(models.Model):
    """Base model with common fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class ExampleModel(BaseModel):
    """Example model for demonstration"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
''',
                    "api.py": '''"""
API endpoints for Django application
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import ExampleModel

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    })

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_example(request):
    """Example API endpoint"""
    if request.method == "GET":
        return JsonResponse({
            "message": "Hello from Django API",
            "method": "GET"
        })
    elif request.method == "POST":
        data = json.loads(request.body)
        return JsonResponse({
            "message": "Data received",
            "data": data,
            "method": "POST"
        })
'''
                }
            },
            "test_code": {
                "success": True,
                "test_files": {
                    "test_main.py": '''"""
Test cases for main application
"""

import unittest
from django.test import TestCase
from django.urls import reverse

class MainAppTestCase(TestCase):
    """Test cases for main application functionality"""
    
    def setUp(self):
        """Set up test data"""
        pass
    
    def test_home_page(self):
        """Test home page loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())
''',
                    "test_utils.py": '''"""
Test cases for utility functions
"""

import unittest
from utils import validate_input, format_response

class UtilsTestCase(unittest.TestCase):
    """Test cases for utility functions"""
    
    def test_validate_input_valid(self):
        """Test input validation with valid data"""
        data = {"key": "value"}
        self.assertTrue(validate_input(data))
    
    def test_validate_input_invalid(self):
        """Test input validation with invalid data"""
        data = "not a dict"
        self.assertFalse(validate_input(data))
    
    def test_format_response(self):
        """Test response formatting"""
        data = {"test": "data"}
        response = format_response(data)
        
        self.assertIn("success", response)
        self.assertIn("data", response)
        self.assertIn("timestamp", response)
        self.assertTrue(response["success"])
        self.assertEqual(response["data"], data)

if __name__ == '__main__':
    unittest.main()
''',
                    "test_models.py": '''"""
Test cases for database models
"""

from django.test import TestCase
from .models import ExampleModel

class ExampleModelTestCase(TestCase):
    """Test cases for ExampleModel"""
    
    def test_model_creation(self):
        """Test model creation"""
        model = ExampleModel.objects.create(
            name="Test Model",
            description="Test Description"
        )
        self.assertEqual(model.name, "Test Model")
        self.assertEqual(model.description, "Test Description")
        self.assertTrue(model.is_active)
    
    def test_model_str_representation(self):
        """Test string representation"""
        model = ExampleModel.objects.create(name="Test Model")
        self.assertEqual(str(model), "Test Model")
''',
                    "conftest.py": '''"""
Pytest configuration and fixtures
"""

import pytest
from django.conf import settings

@pytest.fixture
def example_data():
    """Fixture for example data"""
    return {
        "name": "Test Example",
        "description": "Test Description",
        "is_active": True
    }

@pytest.fixture
def api_client():
    """Fixture for API client"""
    from rest_framework.test import APIClient
    return APIClient()
'''
                }
            },
            "additional_files": {
                "success": True,
                "additional_files": {
                    "requirements.txt": '''# Django Project Dependencies

# Core Django
Django==4.2.7
djangorestframework==3.14.0

# Database
psycopg2-binary==2.9.7

# Development
pytest==7.4.3
pytest-django==4.5.2
black==23.9.1
flake8==6.1.0

# Production
gunicorn==21.2.0
whitenoise==6.5.0

# Environment
python-dotenv==1.0.0
''',
                    "README.md": f'''# Django Project

{requirement}

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Start development server:
```bash
python manage.py runserver
```

## Testing

Run tests with:
```bash
pytest
```

## Deployment

Use the provided Dockerfile and docker-compose.yml for deployment.
''',
                    ".env.example": '''# Django Environment Variables

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Static Files
STATIC_URL=/static/
STATIC_ROOT=staticfiles/

# Logging
LOG_LEVEL=INFO
''',
                    ".gitignore": '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
''',
                    "Dockerfile": '''# Django Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
''',
                    "docker-compose.yml": '''# Django Docker Compose

version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://postgres:password@db:5432/django_db
    depends_on:
      - db
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=django_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
  static_volume:
  media_volume:
''',
                    "Makefile": '''# Django Makefile

.PHONY: help install test run clean

help:
	@echo "Available commands:"
	@echo "  install  - Install dependencies"
	@echo "  test     - Run tests"
	@echo "  run      - Start development server"
	@echo "  clean    - Clean up files"

install:
	pip install -r requirements.txt

test:
	pytest

run:
	python manage.py runserver

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
''',
                    "scripts/deploy.sh": '''#!/bin/bash

# Django Deployment Script

echo "Starting deployment..."

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start the application
gunicorn --bind 0.0.0.0:8000 config.wsgi:application
''',
                    "docs/API.md": '''# Django API Documentation

## Endpoints

### Health Check
- **GET** `/health/`
- Returns application health status

### Example API
- **GET** `/api/example/`
- Returns example data
- **POST** `/api/example/`
- Accepts JSON data and returns confirmation

## Authentication

Currently, no authentication is required for these endpoints.

## Response Format

All responses are in JSON format:

```json
{
    "status": "success",
    "data": {},
    "timestamp": "2024-01-01T00:00:00Z"
}
```
'''
                }
            }
        }
    elif "React" in tech_stack_name or "Node.js" in tech_stack_name:
        return {
            "main_code": {
                "success": True,
                "files": {
                    "server.js": f'''/*
{requirement}

Node.js/Express Server
*/

const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
const config = require('./config');
const logger = require('./utils/logger');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({{ extended: true }}));

// Database connection
mongoose.connect(config.database.url, {{
    useNewUrlParser: true,
    useUnifiedTopology: true
}})
.then(() => logger.info('Connected to MongoDB'))
.catch(err => logger.error('MongoDB connection error:', err));

// Routes
app.use('/api', require('./routes'));

// Health check
app.get('/health', (req, res) => {{
    res.json({{
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    }});
}});

// Error handling middleware
app.use((err, req, res, next) => {{
    logger.error(err.stack);
    res.status(500).json({{ error: 'Something went wrong!' }});
}});

const PORT = config.port || 3000;
app.listen(PORT, () => {{
    logger.info(`Server running on port ${{PORT}}`);
}});

module.exports = app;
''',
                    "config/index.js": '''/*
Configuration for the application
*/

const env = process.env.NODE_ENV || 'development';

const config = {
    development: {
        port: 3000,
        database: {
            url: 'mongodb://localhost:27017/dev_db'
        },
        cors: {
            origin: 'http://localhost:3000'
        },
        jwt: {
            secret: 'dev-secret-key',
            expiresIn: '24h'
        }
    },
    production: {
        port: process.env.PORT || 3000,
        database: {
            url: process.env.MONGODB_URI
        },
        cors: {
            origin: process.env.ALLOWED_ORIGINS?.split(',') || []
        },
        jwt: {
            secret: process.env.JWT_SECRET,
            expiresIn: '24h'
        }
    }
};

module.exports = config[env];
''',
                    "utils/logger.js": '''/*
Logging utility
*/

const winston = require('winston');

const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
    ),
    defaultMeta: { service: 'api-service' },
    transports: [
        new winston.transports.File({ filename: 'error.log', level: 'error' }),
        new winston.transports.File({ filename: 'combined.log' })
    ]
});

if (process.env.NODE_ENV !== 'production') {
    logger.add(new winston.transports.Console({
        format: winston.format.simple()
    }));
}

module.exports = logger;
''',
                    "utils/validator.js": '''/*
Input validation utilities
*/

const Joi = require('joi');

const validateInput = (data, schema) => {
    const { error, value } = schema.validate(data);
    if (error) {
        throw new Error(error.details[0].message);
    }
    return value;
};

const formatResponse = (data, success = true) => {
    return {
        success,
        data,
        timestamp: new Date().toISOString()
    };
};

module.exports = {
    validateInput,
    formatResponse
};
''',
                    "models/User.js": '''/*
User model
*/

const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
    username: {
        type: String,
        required: true,
        unique: true,
        trim: true
    },
    email: {
        type: String,
        required: true,
        unique: true,
        lowercase: true
    },
    password: {
        type: String,
        required: true
    },
    isActive: {
        type: Boolean,
        default: true
    }
}, {
    timestamps: true
});

module.exports = mongoose.model('User', userSchema);
''',
                    "routes/index.js": '''/*
Main routes
*/

const express = require('express');
const router = express.Router();

const userRoutes = require('./users');
const authRoutes = require('./auth');

router.use('/users', userRoutes);
router.use('/auth', authRoutes);

module.exports = router;
''',
                    "routes/users.js": '''/*
User routes
*/

const express = require('express');
const router = express.Router();
const User = require('../models/User');
const { validateInput } = require('../utils/validator');

// Get all users
router.get('/', async (req, res) => {
    try {
        const users = await User.find({ isActive: true });
        res.json({ success: true, data: users });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Get user by ID
router.get('/:id', async (req, res) => {
    try {
        const user = await User.findById(req.params.id);
        if (!user) {
            return res.status(404).json({ success: false, error: 'User not found' });
        }
        res.json({ success: true, data: user });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

module.exports = router;
''',
                    "routes/auth.js": '''/*
Authentication routes
*/

const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const config = require('../config');

// Register
router.post('/register', async (req, res) => {
    try {
        const { username, email, password } = req.body;
        
        // Check if user exists
        const existingUser = await User.findOne({ $or: [{ email }, { username }] });
        if (existingUser) {
            return res.status(400).json({ success: false, error: 'User already exists' });
        }
        
        // Hash password
        const hashedPassword = await bcrypt.hash(password, 10);
        
        // Create user
        const user = new User({
            username,
            email,
            password: hashedPassword
        });
        
        await user.save();
        
        res.status(201).json({ success: true, message: 'User created successfully' });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Login
router.post('/login', async (req, res) => {
    try {
        const { email, password } = req.body;
        
        // Find user
        const user = await User.findOne({ email });
        if (!user) {
            return res.status(401).json({ success: false, error: 'Invalid credentials' });
        }
        
        // Check password
        const isValidPassword = await bcrypt.compare(password, user.password);
        if (!isValidPassword) {
            return res.status(401).json({ success: false, error: 'Invalid credentials' });
        }
        
        // Generate token
        const token = jwt.sign(
            { userId: user._id, email: user.email },
            config.jwt.secret,
            { expiresIn: config.jwt.expiresIn }
        );
        
        res.json({ success: true, token });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

module.exports = router;
'''
                }
            },
            "test_code": {
                "success": True,
                "test_files": {
                    "test/server.test.js": '''/*
Server tests
*/

const request = require('supertest');
const app = require('../server');
const mongoose = require('mongoose');

describe('Server', () => {
    beforeAll(async () => {
        // Connect to test database
        await mongoose.connect('mongodb://localhost:27017/test_db');
    });

    afterAll(async () => {
        await mongoose.connection.close();
    });

    describe('GET /health', () => {
        it('should return health status', async () => {
            const response = await request(app).get('/health');
            expect(response.statusCode).toBe(200);
            expect(response.body.status).toBe('healthy');
            expect(response.body.timestamp).toBeDefined();
        });
    });
});
''',
                    "test/routes/users.test.js": '''/*
User routes tests
*/

const request = require('supertest');
const app = require('../server');
const User = require('../models/User');

describe('User Routes', () => {
    beforeEach(async () => {
        await User.deleteMany({});
    });

    describe('GET /api/users', () => {
        it('should return empty array when no users', async () => {
            const response = await request(app).get('/api/users');
            expect(response.statusCode).toBe(200);
            expect(response.body.success).toBe(true);
            expect(response.body.data).toEqual([]);
        });
    });
});
''',
                    "test/routes/auth.test.js": '''/*
Auth routes tests
*/

const request = require('supertest');
const app = require('../server');
const User = require('../models/User');

describe('Auth Routes', () => {
    beforeEach(async () => {
        await User.deleteMany({});
    });

    describe('POST /api/auth/register', () => {
        it('should create new user', async () => {
            const userData = {
                username: 'testuser',
                email: 'test@example.com',
                password: 'password123'
            };

            const response = await request(app)
                .post('/api/auth/register')
                .send(userData);

            expect(response.statusCode).toBe(201);
            expect(response.body.success).toBe(true);
        });
    });
});
''',
                    "test/utils/validator.test.js": '''/*
Validator tests
*/

const { validateInput, formatResponse } = require('../../utils/validator');
const Joi = require('joi');

describe('Validator', () => {
    describe('validateInput', () => {
        it('should validate correct data', () => {
            const schema = Joi.object({
                name: Joi.string().required(),
                email: Joi.string().email().required()
            });

            const data = {
                name: 'Test User',
                email: 'test@example.com'
            };

            const result = validateInput(data, schema);
            expect(result).toEqual(data);
        });

        it('should throw error for invalid data', () => {
            const schema = Joi.object({
                name: Joi.string().required(),
                email: Joi.string().email().required()
            });

            const data = {
                name: 'Test User',
                email: 'invalid-email'
            };

            expect(() => validateInput(data, schema)).toThrow();
        });
    });

    describe('formatResponse', () => {
        it('should format response correctly', () => {
            const data = { test: 'data' };
            const response = formatResponse(data);

            expect(response.success).toBe(true);
            expect(response.data).toEqual(data);
            expect(response.timestamp).toBeDefined();
        });
    });
});
'''
                }
            },
            "additional_files": {
                "success": True,
                "additional_files": {
                    "package.json": '''{
  "name": "nodejs-api",
  "version": "1.0.0",
  "description": "Node.js API with Express and MongoDB",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "test": "jest",
    "test:watch": "jest --watch"
  },
  "dependencies": {
    "express": "^4.18.2",
    "mongoose": "^7.5.0",
    "cors": "^2.8.5",
    "bcryptjs": "^2.4.3",
    "jsonwebtoken": "^9.0.2",
    "joi": "^17.9.2",
    "winston": "^3.10.0",
    "dotenv": "^16.3.1"
  },
  "devDependencies": {
    "jest": "^29.6.2",
    "supertest": "^6.3.3",
    "nodemon": "^3.0.1"
  },
  "keywords": ["nodejs", "express", "mongodb", "api"],
  "author": "Your Name",
  "license": "MIT"
}''',
                    "README.md": f'''# Node.js API Project

{requirement}

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
```

3. Start development server:
```bash
npm run dev
```

## Testing

Run tests with:
```bash
npm test
```

## API Endpoints

- `GET /health` - Health check
- `GET /api/users` - Get all users
- `GET /api/users/:id` - Get user by ID
- `POST /api/auth/register`
- `POST /api/auth/login`

## Deployment

Use the provided Dockerfile and docker-compose.yml for deployment.
''',
                    ".env.example": '''# Node.js Environment Variables

# Server
PORT=3000
NODE_ENV=development

# Database
MONGODB_URI=mongodb://localhost:27017/dev_db

# JWT
JWT_SECRET=your-secret-key-here

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
''',
                    ".gitignore": '''# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
logs
*.log

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
''',
                    "Dockerfile": '''# Node.js Dockerfile

FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
''',
                    "docker-compose.yml": '''# Node.js Docker Compose

version: '3.8'

services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - MONGODB_URI=mongodb://mongo:27017/prod_db
      - JWT_SECRET=your-production-secret
    depends_on:
      - mongo
    volumes:
      - .:/app
      - /app/node_modules

  mongo:
    image: mongo:6
    environment:
      - MONGO_INITDB_DATABASE=prod_db
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
''',
                    "jest.config.js": '''module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/test/**/*.test.js'],
  collectCoverageFrom: [
    '**/*.js',
    '!**/node_modules/**',
    '!**/test/**'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov']
};
''',
                    "Makefile": '''# Node.js Makefile

.PHONY: help install test run clean

help:
	@echo "Available commands:"
	@echo "  install  - Install dependencies"
	@echo "  test     - Run tests"
	@echo "  run      - Start development server"
	@echo "  clean    - Clean up files"

install:
	npm install

test:
	npm test

run:
	npm run dev

clean:
	rm -rf node_modules
	rm -rf coverage
	find . -name "*.log" -delete
''',
                    "scripts/deploy.sh": '''#!/bin/bash

# Node.js Deployment Script

echo "Starting deployment..."

# Install dependencies
npm ci --only=production

# Run tests
npm test

# Start the application
npm start
''',
                    "docs/API.md": '''# Node.js API Documentation

## Authentication

Most endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Health Check
- **GET** `/health`
- Returns application health status

### Users
- **GET** `/api/users`
- Get all active users
- **GET** `/api/users/:id`
- Get user by ID

### Authentication
- **POST** `/api/auth/register`
- Register new user
- **POST** `/api/auth/login`
- Login user

## Request/Response Format

### Register Request
```json
{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
}
```

### Login Request
```json
{
    "email": "test@example.com",
    "password": "password123"
}
```

### Response Format
```json
{
    "success": true,
    "data": {},
    "timestamp": "2024-01-01T00:00:00Z"
}
```
'''
                }
            }
        }
    else:
        # Default Python template
        return {
            "main_code": {
                "success": True,
                "files": {
                    "main.py": f'''"""
{requirement}

Python Application Template
"""

import logging
from typing import Dict, Any
from utils import setup_logging, validate_input, format_response

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class Application:
    """Main application class"""
    
    def __init__(self):
        self.name = "AI-Generated Application"
        logger.info("Initializing " + self.name)
    
    def process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming request"""
        if not validate_input(data):
            return format_response({{"error": "Invalid input"}})
        
        try:
            # Process the data here
            result = {{"processed": True, "data": data}}
            logger.info("Request processed successfully")
            return format_response(result)
        except Exception as e:
            logger.error("Error processing request: " + str(e))
            return format_response({{"error": str(e)}})
    
    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return format_response({{"status": "healthy"}})

def main():
    """Main function"""
    app = Application()
    
    # Example usage
    sample_data = {{"key": "value"}}
    result = app.process_request(sample_data)
    print(result)
    
    health = app.health_check()
    print(health)

if __name__ == "__main__":
    main()
''',
                    "config.py": '''"""
Configuration settings
"""

import os
from typing import Dict, Any

class Config:
    """Base configuration class"""
    
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get configuration dictionary"""
        return {
            'debug': Config.DEBUG,
            'secret_key': Config.SECRET_KEY,
            'database_url': Config.DATABASE_URL
        }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
''',
                    "utils.py": '''"""
Utility functions
"""

import logging
from typing import Any, Dict

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def validate_input(data: Dict[str, Any]) -> bool:
    """Validate input data"""
    if not isinstance(data, dict):
        return False
    return True

def format_response(data: Any) -> Dict[str, Any]:
    """Format response data"""
    return {
        "success": True,
        "data": data,
        "timestamp": "2024-01-01T00:00:00Z"
    }
'''
                }
            },
            "test_code": {
                "success": True,
                "test_files": {
                    "test_main.py": '''"""
Test cases for main application
"""

import unittest
from main import Application

class ApplicationTestCase(unittest.TestCase):
    """Test cases for Application class"""
    
    def setUp(self):
        """Set up test data"""
        self.app = Application()
    
    def test_health_check(self):
        """Test health check method"""
        result = self.app.health_check()
        self.assertIn('success', result)
        self.assertTrue(result['success'])
        self.assertIn('data', result['data'])
    
    def test_process_request_valid(self):
        """Test process_request with valid data"""
        data = {"key": "value"}
        result = self.app.process_request(data)
        self.assertIn('success', result)
        self.assertTrue(result['success'])
        self.assertIn('data', result['data'])
    
    def test_process_request_invalid(self):
        """Test process_request with invalid data"""
        data = "not a dict"
        result = self.app.process_request(data)
        self.assertIn('success', result)
        self.assertTrue(result['success'])
        self.assertIn('error', result['data'])

if __name__ == '__main__':
    unittest.main()
''',
                    "test_utils.py": '''"""
Test cases for utility functions
"""

import unittest
from utils import validate_input, format_response

class UtilsTestCase(unittest.TestCase):
    """Test cases for utility functions"""
    
    def test_validate_input_valid(self):
        """Test input validation with valid data"""
        data = {"key": "value"}
        self.assertTrue(validate_input(data))
    
    def test_validate_input_invalid(self):
        """Test input validation with invalid data"""
        data = "not a dict"
        self.assertFalse(validate_input(data))
    
    def test_format_response(self):
        """Test response formatting"""
        data = {"test": "data"}
        response = format_response(data)
        
        self.assertIn("success", response)
        self.assertIn("data", response)
        self.assertIn("timestamp", response)
        self.assertTrue(response["success"])
        self.assertEqual(response["data"], data)

if __name__ == '__main__':
    unittest.main()
'''
                }
            }
        }

def generate_project_structure(selected_tech_stack, requirement_text, ai_engine, model="gpt-4o-mini"):
    """Generate project file structure based on selected tech stack"""
    try:
        prompt = f"""
        You are a software architect. Based on the selected tech stack and requirements, generate a detailed project file structure.

        Selected Tech Stack: {selected_tech_stack}
        Requirements: {requirement_text}

        Create a comprehensive project structure including:
        1. Directory structure with all necessary folders
        2. File names and their purposes
        3. Configuration files needed
        4. Dependencies and requirements files
        5. Documentation files
        6. Testing structure
        7. Deployment files

        CRITICAL: You must respond with ONLY a valid JSON object. Follow these rules:
        - Use proper JSON syntax with commas between all array elements
        - Use proper JSON syntax with commas between all object properties
        - No trailing commas
        - No additional text, explanations, or markdown formatting
        - Ensure all strings are properly quoted
        - Ensure all brackets and braces are properly closed

        Example format:
        {{
            "success": true,
            "project_name": "suggested project name",
            "structure": {{
                "root_files": ["file1", "file2", "file3"],
                "directories": {{
                    "src/": ["main.py", "config.py", "utils.py"],
                    "tests/": ["test_main.py", "test_utils.py"],
                    "docs/": ["README.md", "API.md"],
                    "config/": ["settings.py", "database.py"],
                    "scripts/": ["deploy.sh", "setup.py"]
                }}
            }},
            "dependencies": {{
                "main": ["dependency1", "dependency2"],
                "dev": ["dev-dependency1", "dev-dependency2"],
                "test": ["test-dependency1", "test-dependency2"]
            }},
            "description": "Brief project description"
        }}

        Remember: Every array element must be separated by commas, and every object property must be separated by commas.
        """
        
        response = ai_engine.generate_response(prompt, model=model)
        
        # Try to parse JSON from response
        try:
            import json
            import re
            
            # Clean the response - remove any markdown formatting
            cleaned_response = response.strip()
            
            # Remove markdown code blocks if present
            cleaned_response = re.sub(r'```json\s*', '', cleaned_response)
            cleaned_response = re.sub(r'```\s*$', '', cleaned_response)
            
            # Find JSON object
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = cleaned_response[start_idx:end_idx]
                
                # Try to repair common JSON issues
                try:
                    result = json.loads(json_str)
                except json.JSONDecodeError:
                    # Try to fix common JSON formatting issues
                    fixed_json = json_str
                    
                    # Fix missing commas in arrays
                    fixed_json = re.sub(r'(\w+)\s*\n\s*(\w+)', r'\1,\n\2', fixed_json)
                    fixed_json = re.sub(r'(\w+)\s*"(\w+)"', r'\1, "\2"', fixed_json)
                    
                    # Fix missing commas in objects
                    fixed_json = re.sub(r'(\w+)\s*\n\s*"(\w+)":', r'\1,\n"\2":', fixed_json)
                    
                    # Fix trailing commas
                    fixed_json = re.sub(r',\s*}', '}', fixed_json)
                    fixed_json = re.sub(r',\s*]', ']', fixed_json)
                    
                    # Try parsing the fixed JSON
                    try:
                        result = json.loads(fixed_json)
                    except json.JSONDecodeError:
                        # If still failing, try a more aggressive fix
                        # Remove any lines that don't look like valid JSON
                        lines = fixed_json.split('\n')
                        cleaned_lines = []
                        for line in lines:
                            line = line.strip()
                            if (line.startswith('"') or line.startswith('{') or 
                                line.startswith('}') or line.startswith('[') or 
                                line.startswith(']') or line.startswith(',') or
                                ':' in line):
                                cleaned_lines.append(line)
                        
                        fixed_json = '\n'.join(cleaned_lines)
                        
                        try:
                            result = json.loads(fixed_json)
                        except json.JSONDecodeError as final_error:
                            st.error(f"Failed to parse project structure response as JSON: {str(final_error)}")
                            st.error("Raw response preview:")
                            st.code(response[:500] + "..." if len(response) > 500 else response)
                            return {"success": False, "error": f"JSON parsing error: {str(final_error)}"}
                
                # Validate the structure
                if isinstance(result, dict) and result.get("success") is not None:
                    return result
                else:
                    return {"success": False, "error": "Invalid project structure response format"}
            else:
                # Try parsing the entire response as JSON
                result = json.loads(cleaned_response)
                if isinstance(result, dict) and result.get("success") is not None:
                    return result
                else:
                    return {"success": False, "error": "Response is not a valid JSON object"}
                    
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse project structure response as JSON: {str(e)}")
            st.error("Raw response preview:")
            st.code(response[:500] + "..." if len(response) > 500 else response)
            return {"success": False, "error": f"JSON parsing error: {str(e)}"}
            
    except Exception as e:
        handle_and_display_error(e, "generate_project_structure")
        return {"success": False, "error": str(e)}

def generate_code_for_structure(project_structure, requirement_text, ai_engine, model="gpt-4o-mini"):
    """Generate complete project files based on project structure"""
    try:
        # Parse the project structure to understand what files to generate
        import json
        project_data = json.loads(project_structure) if isinstance(project_structure, str) else project_structure
        
        # Extract file structure from the project data
        file_structure = project_data.get('file_structure', {})
        
        # Generate all files according to the structure
        all_files = {}
        
        # Generate main application files
        main_files_prompt = f"""
        Based on the project structure and requirements, generate ALL the main application files:
        
        Project Structure: {project_structure}
        Requirements: {requirement_text}
        
        Generate complete implementation for ALL files in the project structure with:
        1. Complete implementation for each file
        2. Proper imports and dependencies
        3. Error handling
        4. Documentation and docstrings
        5. Type hints where applicable
        6. Best practices and design patterns
        7. Configuration management
        8. Logging setup
        9. Database models if needed
        10. API endpoints if needed
        11. Utility functions
        12. Constants and settings
        
        Return ONLY a valid JSON object with ALL files:
        {{
            "success": true,
            "files": {{
                "main.py": "complete main application code",
                "config.py": "complete configuration code",
                "utils.py": "complete utility functions",
                "models.py": "database models if needed",
                "api.py": "API endpoints if needed",
                "constants.py": "constants and settings",
                "logger.py": "logging configuration",
                "requirements.txt": "dependencies list",
                "README.md": "project documentation",
                ".env.example": "environment variables template",
                "Dockerfile": "container configuration if needed",
                "docker-compose.yml": "docker compose if needed"
            }}
        }}
        
        Ensure the response is valid JSON without any additional text or formatting.
        Generate ALL files that would be needed for a complete, production-ready project.
        """
        
        main_response = ai_engine.generate_response(main_files_prompt, model=model)
        
        # Parse main response
        try:
            import re
            
            # Clean the response
            cleaned_response = main_response.strip()
            cleaned_response = re.sub(r'```json\s*', '', cleaned_response)
            cleaned_response = re.sub(r'```\s*$', '', cleaned_response)
            
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = cleaned_response[start_idx:end_idx]
                main_parsed = json.loads(json_str)
            else:
                main_parsed = json.loads(cleaned_response)
        except json.JSONDecodeError:
            # If JSON parsing fails, treat the response as raw code
            main_parsed = {
                "success": True, 
                "raw": main_response,
                "files": {
                    "main.py": main_response
                }
            }
        
        # Generate test files for all components
        test_files_prompt = f"""
        Generate comprehensive test files for ALL components of the project:
        
        Project Structure: {project_structure}
        Main Code: {main_response}
        
        Create test files for ALL components with:
        1. Unit tests for all functions and classes
        2. Integration tests
        3. Test fixtures and mocks
        4. Edge cases and error scenarios
        5. Performance tests if applicable
        6. API tests if applicable
        7. Database tests if applicable
        
        Return ONLY a valid JSON object:
        {{
            "success": true,
            "test_files": {{
                "test_main.py": "main application tests",
                "test_utils.py": "utility function tests",
                "test_models.py": "database model tests",
                "test_api.py": "API endpoint tests",
                "test_config.py": "configuration tests",
                "test_integration.py": "integration tests",
                "conftest.py": "pytest configuration and fixtures",
                "test_requirements.txt": "test dependencies"
            }}
        }}
        
        Ensure the response is valid JSON without any additional text or formatting.
        Generate tests for ALL files in the project structure.
        """
        
        test_response = ai_engine.generate_response(test_files_prompt, model=model)
        
        # Parse test response
        try:
            # Clean the response
            cleaned_response = test_response.strip()
            cleaned_response = re.sub(r'```json\s*', '', cleaned_response)
            cleaned_response = re.sub(r'```\s*$', '', cleaned_response)
            
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = cleaned_response[start_idx:end_idx]
                test_parsed = json.loads(json_str)
            else:
                test_parsed = json.loads(cleaned_response)
        except json.JSONDecodeError:
            # If JSON parsing fails, treat the response as raw test code
            test_parsed = {
                "success": True, 
                "raw": test_response,
                "test_files": {
                    "test_main.py": test_response
                }
            }
        
        # Generate additional project files
        additional_files_prompt = f"""
        Generate additional project files for a complete, production-ready project:
        
        Project Structure: {project_structure}
        Requirements: {requirement_text}
        
        Generate these additional files:
        1. requirements.txt - Complete dependency list
        2. README.md - Comprehensive project documentation
        3. .env.example - Environment variables template
        4. .gitignore - Git ignore file
        5. setup.py or pyproject.toml - Package configuration
        6. Dockerfile - Container configuration
        7. docker-compose.yml - Docker compose setup
        8. Makefile - Build and deployment commands
        9. scripts/ - Deployment and utility scripts
        10. docs/ - Additional documentation
        
        Return ONLY a valid JSON object:
        {{
            "success": true,
            "additional_files": {{
                "requirements.txt": "complete dependency list",
                "README.md": "comprehensive documentation",
                ".env.example": "environment variables",
                ".gitignore": "git ignore patterns",
                "setup.py": "package configuration",
                "Dockerfile": "container configuration",
                "docker-compose.yml": "docker compose setup",
                "Makefile": "build commands",
                "scripts/deploy.sh": "deployment script",
                "docs/API.md": "API documentation"
            }}
        }}
        
        Ensure the response is valid JSON without any additional text or formatting.
        """
        
        additional_response = ai_engine.generate_response(additional_files_prompt, model=model)
        
        # Parse additional response
        try:
            # Clean the response
            cleaned_response = additional_response.strip()
            cleaned_response = re.sub(r'```json\s*', '', cleaned_response)
            cleaned_response = re.sub(r'```\s*$', '', cleaned_response)
            
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = cleaned_response[start_idx:end_idx]
                additional_parsed = json.loads(json_str)
            else:
                additional_parsed = json.loads(cleaned_response)
        except json.JSONDecodeError:
            # If JSON parsing fails, create basic additional files
            additional_parsed = {
                "success": True,
                "additional_files": {
                    "requirements.txt": "# Project Dependencies\n\n# Add your dependencies here",
                    "README.md": f"# Project\n\n{requirement_text}",
                    ".env.example": "# Environment Variables\n\n# Add your environment variables here",
                    ".gitignore": "# Python\n__pycache__/\n*.pyc\n.env\nvenv/\n"
                }
            }
        
        return {
            "success": True,
            "main_code": main_parsed,
            "test_code": test_parsed,
            "additional_files": additional_parsed
        }
    except Exception as e:
        handle_and_display_error(e, "generate_code_for_structure")
        return {"success": False, "error": str(e)}

# Main application
def main():
    st.markdown('<h1 class="main-header">AI-Powered Development Assistant</h1>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.markdown("""
            <div style='padding: 18px 16px 12px 16px; background: #f7f7fa; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.04); margin-bottom: 18px;'>
                <h3 style='margin-bottom: 8px; color: #222;'>Configuration</h3>
                <p style='font-size: 0.95em; color: #555; margin-bottom: 18px;'>
                    Select your preferred AI model and adjust generation settings for optimal results.
                </p>
        """, unsafe_allow_html=True)

        # Model selection
        model = st.selectbox(
            "AI Model",
            ["Gemini 2.5 Pro", "gpt-4o-mini", "gpt-4o"],
            index=0,
            help="Choose the AI model for code and test generation."
        )

        # Temperature setting
        temperature = st.slider(
            "Creativity Level",
            0.0, 1.0, 0.7, 0.1,
            help="Controls randomness. Lower values = more deterministic, higher = more creative."
        )

        # Max tokens
        max_tokens = st.slider(
            "Max Response Length",
            1000, 4000, 2000, 500,
            help="Maximum number of tokens (words/pieces) in the AI's response."
        )

        st.markdown("""
            <div style='font-size: 0.92em; color: #888; margin-top: 10px;'>
                <b>Tip:</b> For most use cases, the default settings work well. Adjust only if you need more control.
            </div>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        # File management
        st.header("Generated Files")
        if st.session_state.generated_files:
            for i, file_info in enumerate(st.session_state.generated_files):
                with st.expander(f"{file_info['name']}"):
                    st.write(f"**Type:** {file_info['type']}")
                    st.write(f"**Created:** {file_info['timestamp']}")
                    if st.button(f"Download {file_info['name']}", key=f"download_{i}_{file_info['name']}"):
                        with open(file_info['path'], 'r') as f:
                            st.download_button(
                                label="Click to download",
                                data=f.read(),
                                file_name=file_info['name'],
                                mime="text/plain"
                            )
        else:
            st.info("No files generated yet")
    
    # Main tabs
    tab1, tab2, tab_error, tab3, tab4, tab5 = st.tabs([
        "Code Generation",
        "Test Generation",
        "Error Logs",
        "Analysis",
        "Deployment Check",
        "File Manager"
    ])
    
    # Tab 1: Code Generation
    with tab1:
        st.header("AI-Powered Code Generation")
        
        # Document upload section
        st.subheader("Upload Requirements Document (Optional)")
        uploaded_file = st.file_uploader(
            "Choose a document",
            type=['pdf', 'docx', 'doc', 'txt'],
            help="Upload PDF, Word, or text files containing your requirements"
        )
        
        # Process uploaded document
        if uploaded_file is not None:
            st.session_state.uploaded_document = process_uploaded_document(uploaded_file)
            if st.session_state.uploaded_document:
                st.success(f"Document processed: {uploaded_file.name}")
                with st.expander("View extracted text"):
                    st.text_area("Document Content", st.session_state.uploaded_document, height=200)
        
        # Requirement input
        st.subheader("Describe Your Requirements")
        requirement_input = st.text_area(
            "Enter your requirements in natural language",
            placeholder="e.g., Create a Python class for a simple calculator that can perform basic arithmetic operations...",
            height=150
        )
        
        # Combine prompt and document
        if st.session_state.uploaded_document and requirement_input:
            combined_requirement = f"""
            Additional Context from Document:
            {st.session_state.uploaded_document}
            
            Specific Requirements:
            {requirement_input}
            """
        elif st.session_state.uploaded_document:
            combined_requirement = st.session_state.uploaded_document
        else:
            combined_requirement = requirement_input
        
        st.session_state.current_requirement = combined_requirement
        
        # Tech stack suggestion
        if st.button("Suggest Tech Stack", type="primary"):
            if combined_requirement.strip():
                with st.spinner("Analyzing requirements and suggesting tech stack..."):
                    tech_stack_options = suggest_tech_stack(combined_requirement, components['ai_engine'], model)
                    if tech_stack_options:
                        st.session_state.tech_stack = tech_stack_options
                        st.markdown('<div class="tech-stack-card">', unsafe_allow_html=True)
                        st.subheader("🎯 Recommended Tech Stack Options")
                        
                        # Create a table for tech stack options
                        tech_data = []
                        for stack in tech_stack_options:
                            tech_data.append({
                                "ID": stack.get('id', 'N/A'),
                                "Name": stack.get('name', 'N/A'),
                                "Language": stack.get('language', 'N/A'),
                                "Framework": stack.get('framework', 'N/A'),
                                "Database": stack.get('database', 'N/A'),
                                "Complexity": stack.get('complexity', 'N/A'),
                                "Est. Time": stack.get('estimated_time', 'N/A')
                            })
                        
                        st.table(tech_data)
                        
                        # Show detailed information for each stack
                        for i, stack in enumerate(tech_stack_options):
                            with st.expander(f"📋 {stack.get('name', 'Tech Stack')} - Details"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.write("**Dependencies:**")
                                    deps = stack.get('dependencies', [])
                                    if isinstance(deps, list):
                                        for dep in deps:
                                            st.write(f"• {dep}")
                                    else:
                                        st.write(f"• {deps}")
                                    
                                    st.write("**Tools:**")
                                    tools = stack.get('tools', [])
                                    if isinstance(tools, list):
                                        for tool in tools:
                                            st.write(f"• {tool}")
                                    else:
                                        st.write(f"• {tools}")
                                
                                with col2:
                                    st.write("**Pros:**")
                                    pros = stack.get('pros', [])
                                    if isinstance(pros, list):
                                        for pro in pros:
                                            st.write(f"• {pro}")
                                    else:
                                        st.write(f"• {pros}")
                                    
                                    st.write("**Cons:**")
                                    cons = stack.get('cons', [])
                                    if isinstance(cons, list):
                                        for con in cons:
                                            st.write(f"• {con}")
                                    else:
                                        st.write(f"• {cons}")
                                
                                st.write(f"**Best Use Case:** {stack.get('best_use_case', 'N/A')}")
                                st.write(f"**Deployment:** {stack.get('deployment', 'N/A')}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("Please enter requirements first")
        
        # Show current tech stack if available
        if st.session_state.tech_stack:
            st.subheader("📋 Available Tech Stack Options")
            tech_data = []
            for stack in st.session_state.tech_stack:
                tech_data.append({
                    "ID": stack.get('id', 'N/A'),
                    "Name": stack.get('name', 'N/A'),
                    "Language": stack.get('language', 'N/A'),
                    "Framework": stack.get('framework', 'N/A'),
                    "Complexity": stack.get('complexity', 'N/A'),
                    "Est. Time": stack.get('estimated_time', 'N/A')
                })
            
            st.table(tech_data)
        
        # Project structure generation
        if st.session_state.tech_stack:
            selected_tech_stack = st.selectbox(
                "Select a Tech Stack for Project Structure",
                options=[ts['name'] for ts in st.session_state.tech_stack],
                index=0
            )
            
            if st.button("Generate Project Structure", type="primary"):
                with st.spinner("Generating project structure..."):
                    try:
                        # Find the selected tech stack by name
                        selected_stack_obj = next(
                            (ts for ts in st.session_state.tech_stack if ts['name'] == selected_tech_stack),
                            None
                        )
                        
                        if selected_stack_obj:
                            project_structure_result = generate_project_structure(
                                json.dumps(selected_stack_obj, indent=2), # Pass as JSON string
                                combined_requirement,
                                components['ai_engine'],
                                model
                            )
                            
                            if project_structure_result['success']:
                                st.success("Project structure generated successfully!")
                                st.subheader("Generated Project Structure")
                                st.json(project_structure_result)
                                
                                # Save project structure
                                project_structure_file = components['file_manager'].save_project_structure_file(
                                    combined_requirement,
                                    project_structure_result
                                )
                                st.session_state.generated_files.append({
                                    'name': os.path.basename(project_structure_file),
                                    'path': project_structure_file,
                                    'type': 'project_structure',
                                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                })
                                st.info(f"Project structure saved to: {project_structure_file}")
                                
                            else:
                                st.error(f"Project structure generation failed: {project_structure_result['error']}")
                        else:
                            st.warning("Please select a tech stack from the list.")
                            
                    except Exception as e:
                        handle_and_display_error(e, "project_structure_tab")
        else:
            st.warning("Please suggest a tech stack first.")
        
        # Code generation based on structure
        if st.session_state.tech_stack and st.session_state.current_requirement:
            if st.button("Generate Code", type="primary"):
                with st.spinner("Generating code..."):
                    try:
                        # Find the selected tech stack by name
                        selected_stack_obj = next(
                            (ts for ts in st.session_state.tech_stack if ts['name'] == selected_tech_stack),
                            None
                        )
                        
                        if selected_stack_obj:
                            # Try AI generation first
                            code_result = generate_code_for_structure(
                                json.dumps(selected_stack_obj, indent=2), # Pass as JSON string
                                combined_requirement,
                                components['ai_engine'],
                                model
                            )
                            
                            # If AI fails, use fallback
                            if not code_result or not code_result.get('success'):
                                st.warning("AI generation failed, using fallback templates...")
                                code_result = _get_fallback_code(selected_stack_obj['name'], combined_requirement)
                            
                            if code_result and code_result.get('success'):
                                st.success("Complete project files generated successfully!")
                                
                                # Extract all file content from JSON responses
                                main_files = {}
                                test_files = {}
                                additional_files = {}
                                
                                # Process main code files
                                if code_result['main_code'].get('success') and code_result['main_code'].get('files'):
                                    main_files = code_result['main_code']['files']
                                elif code_result['main_code'].get('raw'):
                                    main_files = {"main.py": code_result['main_code']['raw']}
                                
                                # Process test code files
                                if code_result['test_code'].get('success') and code_result['test_code'].get('test_files'):
                                    test_files = code_result['test_code']['test_files']
                                elif code_result['test_code'].get('raw'):
                                    test_files = {"test_main.py": code_result['test_code']['raw']}
                                
                                # Process additional files
                                if code_result.get('additional_files') and code_result['additional_files'].get('success'):
                                    additional_files = code_result['additional_files'].get('additional_files', {})
                                
                                # Display file structure
                                st.subheader("Generated Project Structure")
                                
                                # Main files
                                if main_files:
                                    with st.expander("Main Application Files", expanded=True):
                                        for filename, content in main_files.items():
                                            with st.expander(f"{filename}", expanded=False):
                                                st.code(content, language='python' if filename.endswith('.py') else 'text')
                                
                                # Test files
                                if test_files:
                                    with st.expander("Test Files", expanded=False):
                                        for filename, content in test_files.items():
                                            with st.expander(f"{filename}", expanded=False):
                                                st.code(content, language='python' if filename.endswith('.py') else 'text')
                                
                                # Additional files
                                if additional_files:
                                    with st.expander("Project Configuration Files", expanded=False):
                                        for filename, content in additional_files.items():
                                            with st.expander(f"{filename}", expanded=False):
                                                language = 'python' if filename.endswith('.py') else 'markdown' if filename.endswith('.md') else 'text'
                                                st.code(content, language=language)
                                
                                # Save all files
                                saved_files = []
                                
                                # Save main files
                                for filename, content in main_files.items():
                                    file_path = components['file_manager'].save_project_file(
                                        combined_requirement,
                                        filename,
                                        content
                                    )
                                    saved_files.append({
                                        'name': filename,
                                        'path': file_path,
                                        'type': 'code',
                                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    })
                                
                                # Save test files
                                for filename, content in test_files.items():
                                    file_path = components['file_manager'].save_project_file(
                                        combined_requirement,
                                        filename,
                                        content
                                    )
                                    saved_files.append({
                                        'name': filename,
                                        'path': file_path,
                                        'type': 'test',
                                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    })
                                
                                # Save additional files
                                for filename, content in additional_files.items():
                                    file_path = components['file_manager'].save_project_file(
                                        combined_requirement,
                                        filename,
                                        content
                                    )
                                    saved_files.append({
                                        'name': filename,
                                        'path': file_path,
                                        'type': 'config',
                                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    })
                                
                                # Update session state
                                st.session_state.generated_files.extend(saved_files)
                                
                                # Display summary
                                st.success(f"Generated {len(saved_files)} files:")
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Main Files", len(main_files))
                                with col2:
                                    st.metric("Test Files", len(test_files))
                                with col3:
                                    st.metric("Config Files", len(additional_files))
                                
                            else:
                                error_msg = code_result.get('error', 'Unknown error') if code_result else 'No response from AI'
                                handle_and_display_error(Exception(error_msg), "code_generation")
                        else:
                            st.warning("Please select a tech stack from the list.")

                    except Exception as e:
                        handle_and_display_error(e, "code_generation_tab")
        else:
            st.warning("Please generate project structure first.")
    
    # Tab 2: Test Generation
    with tab2:
        st.header("Automated Test Generation")

        st.subheader("Generate Tests for Existing Project")
        uploaded_zip = st.file_uploader("Upload project ZIP", type=["zip"], key="project_zip")
        if uploaded_zip:
            project_dir = extract_project_zip(uploaded_zip)
            if project_dir:
                st.session_state.uploaded_project_path = project_dir
                st.session_state.uploaded_project_files = list_python_files(project_dir)
                st.success("Project uploaded and extracted")

        if st.session_state.uploaded_project_path:
            code_files = st.session_state.uploaded_project_files
            if code_files:
                selected = st.multiselect("Select files for test generation", code_files)
                if st.button("Generate Tests for Uploaded Project") and selected:
                    for file_path in selected:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                code_content = f.read()
                            tr = components['test_generator'].generate_tests(code_content, language='python')
                            if tr['success']:
                                st.success(f"Generated tests for {os.path.basename(file_path)}")
                                st.code(tr['test_code'], language='python')
                                test_file_path = components['file_manager'].save_test_file(os.path.basename(file_path), tr['test_code'])
                                st.session_state.generated_files.append({
                                    'name': os.path.basename(test_file_path),
                                    'path': test_file_path,
                                    'type': 'test',
                                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                })
                                st.info(f"Saved to: {test_file_path}")
                            else:
                                handle_and_display_error(Exception(tr['error']), 'upload_test_generation')
                        except Exception as e:
                            handle_and_display_error(e, 'upload_test_generation')
            st.divider()

        if st.session_state.current_requirement:
            st.info(f"Current requirement: {st.session_state.current_requirement[:100]}...")

            if st.button("Generate Tests", type="primary"):
                with st.spinner("Generating comprehensive test suite..."):
                    try:
                        test_result = components['test_generator'].generate_tests(
                            st.session_state.current_requirement,
                            language="python"
                        )

                        if test_result['success']:
                            st.success("Tests generated successfully!")

                            # Display tests
                            st.subheader("Generated Test Suite")
                            st.code(test_result['test_code'], language='python')

                            # Save test file
                            test_file_path = components['file_manager'].save_test_file(
                                st.session_state.current_requirement,
                                test_result['test_code']
                            )

                            # Update session state
                            st.session_state.generated_files.append({
                                'name': os.path.basename(test_file_path),
                                'path': test_file_path,
                                'type': 'test',
                                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })

                            st.info(f"Tests saved to: {test_file_path}")

                        else:
                            handle_and_display_error(Exception(test_result['error']), "test_generation")

                    except Exception as e:
                        handle_and_display_error(e, "test_generation_tab")
        else:
            st.warning("Please generate code first or enter requirements")

    # Tab: Error Logs
    with tab_error:
        st.header("Error Logs")
        summary = components['error_handler'].get_error_summary()
        st.write(f"Total Errors: {summary['total_errors']}")
        st.write(f"Recovery Rate: {summary['recovery_rate']}%")

        if summary.get('recent_errors'):
            for err in summary['recent_errors']:
                with st.expander(f"{err['timestamp']} - {err['context']}"):
                    st.error(err['error_message'])
                    st.text(err['traceback'])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Error Log"):
                components['error_handler'].clear_error_log()
                st.success("Error log cleared")
        with col2:
            if st.button("Export Error Log"):
                path = components['error_handler'].export_error_log()
                with open(path, 'r') as f:
                    st.download_button(
                        label="Download Error Log",
                        data=f.read(),
                        file_name=os.path.basename(path),
                        mime="application/json"
                    )
    
    # Tab 3: Code Analysis
    with tab3:
        st.header("Code Quality Analysis")
        
        def is_valid_python_file(file_path):
            """Check if a file contains valid Python code (not JSON)."""
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                # Skip empty files
                if not content:
                    return False
                
                # Skip files that start with JSON structure
                if content.startswith('{') or content.startswith('['):
                    return False
                
                # Skip files that contain JSON-like patterns
                if '"success"' in content and '"files"' in content:
                    return False
                
                # Try to parse as Python (basic check)
                try:
                    import ast
                    ast.parse(content)
                    return True
                except SyntaxError:
                    return False
                    
            except Exception:
                return False
        
        # File selection for analysis - only show valid Python files
        code_files = [f for f in st.session_state.generated_files 
                     if f['type'] == 'code' and is_valid_python_file(f['path'])]
        
        if code_files:
            selected_file = st.selectbox(
                "Select code file to analyze",
                options=code_files,
                format_func=lambda x: x['name']
            )
            
            if st.button("Analyze Code", type="primary"):
                with st.spinner("Analyzing code quality..."):
                    try:
                        with open(selected_file['path'], 'r') as f:
                            code_content = f.read()
                        
                        # Debug: Show file content length
                        st.info(f"Analyzing file: {selected_file['name']} ({len(code_content)} characters)")
                        
                        analysis = components['code_analyzer'].analyze_code(code_content)
                        
                        # Debug: Show analysis structure
                        st.write("Analysis result structure:", analysis.keys())
                        
                        # Display analysis results
                        col1, col2 = st.columns(2)
                        metrics = analysis.get('metrics', {})
                        
                        # Debug: Show metrics structure
                        st.write("Metrics structure:", metrics.keys())
                        
                        with col1:
                            st.metric("Complexity Score", f"{metrics.get('complexity_score', 0):.2f}")
                            st.metric("Lines of Code", metrics.get('lines_of_code', 0))
                            st.metric("Functions", metrics.get('functions', 0))
                        with col2:
                            st.metric("Classes", metrics.get('classes', 0))
                            st.metric("Imports", metrics.get('imports', 0))
                            st.metric("Comments", metrics.get('comments', 0))
                        
                        # Additional metrics
                        st.subheader("Quality Metrics")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Quality Score", f"{analysis.get('quality_score', 0):.1f}/100")
                            st.metric("Complexity Level", analysis.get('complexity', 'Unknown').title())
                        
                        with col2:
                            st.metric("Docstrings", metrics.get('docstrings', 0))
                            st.metric("Variables", metrics.get('variables', 0))
                        
                        with col3:
                            st.metric("Characters", metrics.get('characters', 0))
                            st.metric("Language", analysis.get('language', 'Unknown').title())
                        
                        # Issues and suggestions
                        if analysis.get('issues'):
                            st.subheader("Issues Found")
                            for issue in analysis['issues']:
                                st.error(f"• {issue}")
                        
                        if analysis.get('suggestions'):
                            st.subheader("Suggestions")
                            for suggestion in analysis['suggestions']:
                                st.info(f"• {suggestion}")
                        
                        # Detailed analysis
                        with st.expander("Detailed Analysis"):
                            st.json(analysis)
                            
                    except Exception as e:
                        handle_and_display_error(e, "analysis_tab")
        else:
            st.warning("No valid Python code files available for analysis")
    
    # Tab 4: Deployment Check
    with tab4:
        st.header("Deployment Readiness Assessment")
        
        if st.session_state.current_requirement:
            if st.button("Assess Deployment Readiness", type="primary"):
                with st.spinner("Assessing deployment readiness..."):
                    try:
                        # Get the latest generated code for assessment
                        code_content = st.session_state.current_requirement
                        test_content = ""
                        
                        # Try to get actual code files if available
                        code_files = [f for f in st.session_state.generated_files if f['type'] == 'code']
                        test_files = [f for f in st.session_state.generated_files if f['type'] == 'test']
                        
                        if code_files:
                            try:
                                with open(code_files[-1]['path'], 'r') as f:
                                    code_content = f.read()
                            except:
                                pass
                        
                        if test_files:
                            try:
                                with open(test_files[-1]['path'], 'r') as f:
                                    test_content = f.read()
                            except:
                                pass
                        
                        assessment = components['deploy_checker'].assess_deployment_readiness(
                            code_content,
                            test_content,
                            language="python"
                        )
                        
                        if assessment.get('ready_for_deployment') is not None:
                            st.success("Deployment assessment completed!")
                            
                            # Display score
                            score = assessment['overall_score']
                            st.metric("Deployment Readiness Score", f"{score:.1f}/100")
                            
                            # Score interpretation
                            if score >= 80:
                                st.success("Excellent! Your code is ready for deployment")
                            elif score >= 60:
                                st.warning("Good, but some improvements recommended")
                            else:
                                st.error("Significant improvements needed before deployment")
                            
                            # Display detailed scores
                            st.subheader("Detailed Assessment")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.metric("Code Quality", f"{assessment['detailed_scores']['code_quality']:.1f}/100")
                                st.metric("Test Coverage", f"{assessment['detailed_scores']['test_coverage']:.1f}/100")
                                st.metric("Security", f"{assessment['detailed_scores']['security']:.1f}/100")
                            
                            with col2:
                                st.metric("Performance", f"{assessment['detailed_scores']['performance']:.1f}/100")
                                st.metric("Documentation", f"{assessment['detailed_scores']['documentation']:.1f}/100")
                                st.metric("Risk Level", assessment['risk_level'].title())
                            
                            # Display issues and recommendations
                            if assessment['issues']:
                                st.subheader("Issues Found")
                                for issue in assessment['issues']:
                                    st.write(f"• {issue}")
                            
                            if assessment['recommendations']:
                                st.subheader("Recommendations")
                                for rec in assessment['recommendations']:
                                    st.write(f"• {rec}")
                            
                            st.info(f"Estimated fix time: {assessment['estimated_fix_time']}")
                            
                            # Save assessment
                            assessment_file = components['file_manager'].save_assessment_file(
                                st.session_state.current_requirement,
                                assessment
                            )
                            
                            st.session_state.generated_files.append({
                                'name': os.path.basename(assessment_file),
                                'path': assessment_file,
                                'type': 'assessment',
                                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                            
                        else:
                            error_msg = assessment.get('error', 'Unknown error')
                            handle_and_display_error(Exception(error_msg), "deployment_assessment")

                    except Exception as e:
                        handle_and_display_error(e, "deployment_tab")
        else:
            st.warning("Please generate code first or enter requirements")
    
    # Tab 5: File Manager
    with tab5:
        st.header("File Management")
        
        if st.session_state.generated_files:
            st.subheader("Generated Files")
            
            # File statistics
            file_types = {}
            for file_info in st.session_state.generated_files:
                file_type = file_info['type']
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Code Files", file_types.get('code', 0))
            with col2:
                st.metric("Test Files", file_types.get('test', 0))
            with col3:
                st.metric("Assessments", file_types.get('assessment', 0))
            with col4:
                st.metric("Total Files", len(st.session_state.generated_files))
            
            # File list
            for i, file_info in enumerate(st.session_state.generated_files):
                with st.expander(f"{file_info['name']} ({file_info['type']})"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**Created:** {file_info['timestamp']}")
                        st.write(f"**Path:** {file_info['path']}")
                    
                    with col2:
                        if st.button(f"Download", key=f"dl_{i}"):
                            with open(file_info['path'], 'r') as f:
                                st.download_button(
                                    label="Click to download",
                                    data=f.read(),
                                    file_name=file_info['name'],
                                    mime="text/plain"
                                )
                    
                    with col3:
                        if st.button(f"Delete", key=f"del_{i}"):
                            try:
                                os.remove(file_info['path'])
                                st.session_state.generated_files.pop(i)
                                st.success("File deleted successfully!")
                                st.rerun()
                            except Exception as e:
                                handle_and_display_error(e, "file_delete")
            
            # Export all files
            if st.button("Export All Files", type="primary"):
                try:
                    zip_path = components['file_manager'].create_zip_archive(st.session_state.generated_files)
                    with open(zip_path, 'rb') as f:
                        st.download_button(
                            label="Download ZIP Archive",
                            data=f.read(),
                            file_name="generated_files.zip",
                            mime="application/zip"
                        )
                except Exception as e:
                    handle_and_display_error(e, "create_zip_archive")
            
            # Clear all files
            if st.button("Clear All Files", type="secondary"):
                try:
                    for file_info in st.session_state.generated_files:
                        if os.path.exists(file_info['path']):
                            os.remove(file_info['path'])
                    st.session_state.generated_files = []
                    st.success("All files cleared successfully!")
                    st.rerun()
                except Exception as e:
                    handle_and_display_error(e, "clear_files")
        else:
            st.info("No files generated yet. Start by generating some code!")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            AI-Powered Development Assistant | Built with Streamlit and OpenAI/Gemini
        </div>"""
    )

if __name__ == "__main__":
    main() 