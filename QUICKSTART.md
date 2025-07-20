# Quick Start Guide

Get your AI-Powered Development Assistant up and running in minutes!

## 🚀 Quick Setup

### 1. Clone or Download
```bash
git clone <your-repo-url>
cd ProjectTester
```

### 2. Run Setup Script
```bash
python setup.py
```

### 3. Configure API Keys
Edit the `.env` file and add your API keys:
```bash
# Get your API keys from:
# OpenAI: https://platform.openai.com/api-keys
# Google: https://makersuite.google.com/app/apikey

OPENAI_API_KEY=sk-your-openai-key-here
GOOGLE_API_KEY=your-google-key-here
```

### 4. Launch the Application
```bash
streamlit run app.py
```

### 5. Open Your Browser
Navigate to the URL shown in the terminal (usually `http://localhost:8501`)

## 📝 First Use

### 1. Describe Your Requirement
In the "Generate Code" tab, describe what you want to build:
```
Create a Python function that validates email addresses and returns True if valid, False otherwise. Include proper error handling and logging.
```

### 2. Generate Code
Click "🚀 Generate Code" and wait for the AI to create your implementation.

### 3. Review Generated Code
The system will show you:
- Generated Python code
- Code metrics (lines, complexity, etc.)
- Syntax validation results

### 4. Generate Tests
Switch to the "Test Cases" tab and click "🧪 Generate Tests" to create comprehensive test cases.

### 5. Analyze Code Quality
Use the "Analysis" tab to get detailed insights about:
- Code complexity
- Quality metrics
- Security considerations
- Performance analysis

### 6. Check Deployment Readiness
The "Deployment" tab will assess if your code is ready for production deployment.

## 🎯 Example Requirements

Try these example requirements to get started:

### Simple Function
```
Create a function that calculates the factorial of a number with input validation and error handling.
```

### Data Processing
```
Build a class that processes CSV files, validates data, and generates summary statistics with logging.
```

### API Integration
```
Create a Python class that connects to a REST API, handles authentication, and provides methods for GET and POST requests with proper error handling.
```

### Web Scraping
```
Implement a web scraper that extracts product information from an e-commerce site with rate limiting and error recovery.
```

## 🔧 Configuration Options

### AI Models
- **OpenAI GPT-4**: Best for complex logic and detailed implementations
- **Google Gemini Pro**: Good for general code generation and faster responses

### Programming Languages
Currently supports:
- Python (primary)
- JavaScript
- TypeScript
- Java
- C++
- C

### Test Frameworks
- **pytest**: Recommended for Python
- **unittest**: Alternative for Python

## 📊 Understanding Results

### Code Quality Score (0-100)
- **90-100**: Excellent, production-ready
- **70-89**: Good, minor improvements needed
- **50-69**: Fair, significant improvements recommended
- **0-49**: Poor, major refactoring needed

### Deployment Readiness
- **✅ Ready**: Score ≥ 70, minimal issues
- **⚠️ Needs Work**: Score 50-69, moderate issues
- **❌ Not Ready**: Score < 50, major issues

### Risk Levels
- **LOW**: Safe for production deployment
- **MEDIUM**: Requires testing and monitoring
- **HIGH**: Needs significant improvements before deployment

## 🛠️ Troubleshooting

### Common Issues

**"API Key Error"**
- Check your `.env` file has correct API keys
- Verify keys are active and have sufficient credits

**"Import Error"**
- Run `pip install -r requirements.txt`
- Ensure Python 3.8+ is installed

**"Permission Error"**
- Check file permissions in the `generated/` directory
- Run with appropriate user permissions

**"Memory Error"**
- Reduce `MAX_TOKENS` in `.env` file
- Close other applications to free memory

### Getting Help

1. Check the error logs in the sidebar
2. Review the generated error reports
3. Try simpler requirements first
4. Ensure all dependencies are installed

## 🚀 Advanced Features

### Custom Templates
Create custom code templates in the `templates/` directory for specific project patterns.

### Batch Processing
Use the file management features to process multiple requirements at once.

### Integration
The generated code includes proper logging and error handling for easy integration into existing projects.

### Export Options
Download individual files or complete project packages as ZIP files.

## 📈 Best Practices

### Writing Good Requirements
1. **Be Specific**: Include input/output formats, error conditions
2. **Mention Constraints**: Performance, security, compatibility needs
3. **Include Examples**: Provide sample inputs and expected outputs
4. **Specify Dependencies**: Mention required libraries or frameworks

### Code Review Process
1. Review generated code for logic correctness
2. Test with edge cases
3. Verify error handling
4. Check performance implications
5. Ensure security best practices

### Iterative Improvement
1. Start with basic requirements
2. Generate and review code
3. Refine requirements based on results
4. Regenerate with improvements
5. Repeat until satisfied

## 🎉 You're Ready!

Your AI-Powered Development Assistant is now ready to help you build better code faster. Start with simple requirements and gradually explore more complex features as you become familiar with the system.

Happy coding! 🚀 