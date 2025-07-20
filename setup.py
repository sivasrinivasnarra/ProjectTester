#!/usr/bin/env python3
"""
Setup script for AI-Powered Development Assistant
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    directories = [
        "generated/code",
        "generated/tests", 
        "generated/reports",
        "templates"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created successfully")

def setup_environment():
    """Setup environment variables."""
    print("🔧 Setting up environment...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file...")
        with open(env_file, "w") as f:
            f.write("""# AI Model API Keys
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Model Configuration
DEFAULT_MODEL=gpt-4
FALLBACK_MODEL=gemini-pro

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
MAX_TOKENS=4000
TEMPERATURE=0.7

# File Paths
GENERATED_CODE_DIR=generated/code
GENERATED_TESTS_DIR=generated/tests
REPORTS_DIR=generated/reports

# Database
DATABASE_URL=sqlite:///project_tester.db
""")
        print("✅ .env file created")
        print("⚠️  Please update the .env file with your API keys")
    else:
        print("✅ .env file already exists")

def run_tests():
    """Run basic tests to verify installation."""
    print("🧪 Running basic tests...")
    try:
        # Test imports
        import streamlit
        import openai
        import google.generativeai
        import pytest
        import black
        import flake8
        print("✅ All imports successful")
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False
    
    return True

def main():
    """Main setup function."""
    print("🚀 Setting up AI-Powered Development Assistant")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Create directories
    create_directories()
    
    # Setup environment
    setup_environment()
    
    # Run tests
    if run_tests():
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Update .env file with your API keys")
        print("2. Run: streamlit run app.py")
        print("3. Open your browser to the provided URL")
    else:
        print("\n⚠️  Setup completed with warnings")
        print("Please check the error messages above")

if __name__ == "__main__":
    main() 