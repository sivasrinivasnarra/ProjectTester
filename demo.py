#!/usr/bin/env python3
"""
Demo script for AI-Powered Development Assistant
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core import CodeGenerator, TestGenerator, ErrorHandler, DeployChecker
from utils import CodeAnalyzer

def demo_basic_function():
    """Demo with a basic function requirement."""
    print("🧪 Demo: Basic Function Generation")
    print("=" * 50)
    
    requirement = """
    Create a Python function that validates email addresses. 
    The function should:
    - Take an email string as input
    - Return True if valid, False otherwise
    - Include proper error handling
    - Use regex for validation
    - Include logging
    """
    
    print(f"Requirement: {requirement.strip()}")
    print()
    
    # Initialize components
    code_generator = CodeGenerator()
    test_generator = TestGenerator()
    error_handler = ErrorHandler()
    deploy_checker = DeployChecker()
    code_analyzer = CodeAnalyzer()
    
    # Generate code
    print("📝 Generating code...")
    code_result = code_generator.generate_code(requirement)
    
    if code_result["success"]:
        print("✅ Code generated successfully!")
        print(f"📊 Lines of code: {len(code_result['code'].split(chr(10)))}")
        print(f"📁 Saved to: {code_result['file_path']}")
        print()
        
        # Generate tests
        print("🧪 Generating tests...")
        test_result = test_generator.generate_tests(code_result["code"])
        
        if test_result["success"]:
            print("✅ Tests generated successfully!")
            print(f"📊 Test functions: {test_result['test_code'].count('def test_')}")
            print(f"📁 Saved to: {test_result['test_file_path']}")
            print()
            
            # Analyze code
            print("📊 Analyzing code...")
            analysis = code_analyzer.analyze_code(code_result["code"])
            print(f"✅ Analysis completed!")
            print(f"📊 Quality score: {analysis['quality_score']:.1f}/100")
            print(f"📊 Complexity: {analysis['complexity']}")
            print()
            
            # Deployment assessment
            print("🚀 Assessing deployment readiness...")
            assessment = deploy_checker.assess_deployment_readiness(
                code_result["code"], 
                test_result["test_code"]
            )
            print(f"✅ Assessment completed!")
            print(f"📊 Overall score: {assessment.get('overall_score', 0)}/100")
            print(f"📊 Ready for deployment: {assessment.get('ready_for_deployment', False)}")
            print(f"📊 Risk level: {assessment.get('risk_level', 'unknown')}")
            print()
            
            # Display results
            print("📋 Summary:")
            print(f"   Code Quality: {analysis.get('quality_score', 0):.1f}/100")
            print(f"   Deployment Score: {assessment.get('overall_score', 0)}/100")
            print(f"   Ready for Production: {'✅ Yes' if assessment.get('ready_for_deployment', False) else '❌ No'}")
            
            if assessment.get('issues'):
                print("\n⚠️  Issues found:")
                for issue in assessment['issues'][:3]:  # Show first 3
                    print(f"   - {issue}")
            
            if assessment.get('recommendations'):
                print("\n💡 Recommendations:")
                for rec in assessment['recommendations'][:3]:  # Show first 3
                    print(f"   - {rec}")
            
        else:
            print(f"❌ Test generation failed: {test_result.get('error', 'Unknown error')}")
    else:
        print(f"❌ Code generation failed: {code_result.get('error', 'Unknown error')}")

def demo_class_implementation():
    """Demo with a class implementation requirement."""
    print("\n🧪 Demo: Class Implementation")
    print("=" * 50)
    
    requirement = """
    Create a Python class for a simple calculator that:
    - Supports basic operations (add, subtract, multiply, divide)
    - Includes input validation
    - Handles division by zero errors
    - Provides a history of operations
    - Includes logging for debugging
    """
    
    print(f"Requirement: {requirement.strip()}")
    print()
    
    # Initialize components
    code_generator = CodeGenerator()
    test_generator = TestGenerator()
    error_handler = ErrorHandler()
    deploy_checker = DeployChecker()
    code_analyzer = CodeAnalyzer()
    
    # Generate code
    print("📝 Generating code...")
    code_result = code_generator.generate_code(requirement)
    
    if code_result["success"]:
        print("✅ Code generated successfully!")
        print(f"📊 Lines of code: {len(code_result['code'].split(chr(10)))}")
        print()
        
        # Generate tests
        print("🧪 Generating tests...")
        test_result = test_generator.generate_tests(code_result["code"])
        
        if test_result["success"]:
            print("✅ Tests generated successfully!")
            print(f"📊 Test functions: {test_result['test_code'].count('def test_')}")
            print()
            
            # Analyze code
            print("📊 Analyzing code...")
            analysis = code_analyzer.analyze_code(code_result["code"])
            print(f"✅ Analysis completed!")
            print(f"📊 Quality score: {analysis['quality_score']:.1f}/100")
            print(f"📊 Functions: {analysis['metrics'].get('functions', 0)}")
            print(f"📊 Classes: {analysis['metrics'].get('classes', 0)}")
            print()
            
            # Deployment assessment
            print("🚀 Assessing deployment readiness...")
            assessment = deploy_checker.assess_deployment_readiness(
                code_result["code"], 
                test_result["test_code"]
            )
            print(f"✅ Assessment completed!")
            print(f"📊 Overall score: {assessment.get('overall_score', 0)}/100")
            print(f"📊 Ready for deployment: {assessment.get('ready_for_deployment', False)}")
            
            # Display detailed scores
            detailed_scores = assessment.get('detailed_scores', {})
            if detailed_scores:
                print("\n📊 Detailed Scores:")
                for category, score in detailed_scores.items():
                    status = "✅" if score >= 70 else "⚠️" if score >= 50 else "❌"
                    print(f"   {category.replace('_', ' ').title()}: {status} {score}/100")
            
        else:
            print(f"❌ Test generation failed: {test_result.get('error', 'Unknown error')}")
    else:
        print(f"❌ Code generation failed: {code_result.get('error', 'Unknown error')}")

def main():
    """Run the demo."""
    print("🚀 AI-Powered Development Assistant Demo")
    print("=" * 60)
    print()
    
    # Check if API keys are configured
    openai_key = os.getenv('OPENAI_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    
    if not openai_key and not google_key:
        print("⚠️  Warning: No API keys found!")
        print("   The demo will use template-based generation.")
        print("   For full AI capabilities, set OPENAI_API_KEY or GOOGLE_API_KEY")
        print()
    
    # Run demos
    demo_basic_function()
    demo_class_implementation()
    
    print("\n🎉 Demo completed!")
    print("\nTo run the full application:")
    print("   streamlit run app.py")

if __name__ == "__main__":
    main() 