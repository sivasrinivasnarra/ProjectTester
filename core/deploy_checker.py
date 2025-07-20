"""
Deployment Checker module for assessing code readiness for deployment.
"""

import os
import logging
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path
import ast
import re

class DeployChecker:
    """Assesses code readiness for deployment."""
    
    def __init__(self):
        self.check_criteria = {
            "code_quality": 0.3,
            "test_coverage": 0.25,
            "security": 0.2,
            "performance": 0.15,
            "documentation": 0.1
        }
        self.minimum_score = 70  # Minimum score to be deployment ready
    
    def assess_deployment_readiness(self, code: str, tests: str, language: str = "python") -> Dict[str, Any]:
        """Comprehensive assessment of deployment readiness."""
        try:
            assessment = {
                "ready_for_deployment": False,
                "overall_score": 0,
                "detailed_scores": {},
                "issues": [],
                "recommendations": [],
                "risk_level": "high",
                "estimated_fix_time": "unknown"
            }
            
            # Perform individual assessments
            code_quality_score = self._assess_code_quality(code, language)
            test_coverage_score = self._assess_test_coverage(tests, language)
            security_score = self._assess_security(code, language)
            performance_score = self._assess_performance(code, language)
            documentation_score = self._assess_documentation(code, language)
            
            # Calculate weighted overall score
            assessment["detailed_scores"] = {
                "code_quality": code_quality_score,
                "test_coverage": test_coverage_score,
                "security": security_score,
                "performance": performance_score,
                "documentation": documentation_score
            }
            
            overall_score = (
                code_quality_score * self.check_criteria["code_quality"] +
                test_coverage_score * self.check_criteria["test_coverage"] +
                security_score * self.check_criteria["security"] +
                performance_score * self.check_criteria["performance"] +
                documentation_score * self.check_criteria["documentation"]
            )
            
            assessment["overall_score"] = round(overall_score, 2)
            
            # Determine deployment readiness
            assessment["ready_for_deployment"] = overall_score >= self.minimum_score
            
            # Generate issues and recommendations
            assessment["issues"] = self._identify_issues(assessment["detailed_scores"])
            assessment["recommendations"] = self._generate_recommendations(assessment["detailed_scores"])
            
            # Determine risk level
            assessment["risk_level"] = self._determine_risk_level(overall_score)
            
            # Estimate fix time
            assessment["estimated_fix_time"] = self._estimate_fix_time(assessment["issues"])
            
            return assessment
            
        except Exception as e:
            logging.error(f"Error assessing deployment readiness: {e}")
            return {
                "ready_for_deployment": False,
                "error": str(e),
                "overall_score": 0
            }
    
    def _assess_code_quality(self, code: str, language: str) -> float:
        """Assess code quality (0-100)."""
        score = 100.0
        issues = []
        
        try:
            if language.lower() == "python":
                # Check syntax
                ast.parse(code)
                
                # Check for common code quality issues
                lines = code.split('\n')
                
                # Check line length
                long_lines = sum(1 for line in lines if len(line.strip()) > 88)
                if long_lines > 0:
                    score -= (long_lines / len(lines)) * 20
                    issues.append(f"{long_lines} lines exceed 88 characters")
                
                # Check for TODO comments
                todo_count = code.lower().count('todo')
                if todo_count > 0:
                    score -= todo_count * 5
                    issues.append(f"{todo_count} TODO comments found")
                
                # Check for proper imports
                if "import " not in code and "from " not in code:
                    score -= 10
                    issues.append("No imports found")
                
                # Check for error handling
                if "try:" not in code and "except" not in code:
                    score -= 15
                    issues.append("No error handling found")
                
                # Check for logging
                if "logging" not in code and "logger" not in code:
                    score -= 10
                    issues.append("No logging configuration found")
                
                # Check for docstrings
                if '"""' not in code and "'''" not in code:
                    score -= 15
                    issues.append("No docstrings found")
                
        except SyntaxError:
            score = 0
            issues.append("Syntax errors found")
        except Exception as e:
            score -= 20
            issues.append(f"Code analysis error: {e}")
        
        return max(0, score)
    
    def _assess_test_coverage(self, tests: str, language: str) -> float:
        """Assess test coverage (0-100)."""
        score = 100.0
        issues = []
        
        try:
            if language.lower() == "python":
                # Check for test framework imports
                if "pytest" not in tests and "unittest" not in tests:
                    score -= 30
                    issues.append("No testing framework found")
                
                # Check for test functions
                test_functions = len(re.findall(r'def test_', tests))
                if test_functions == 0:
                    score -= 40
                    issues.append("No test functions found")
                elif test_functions < 3:
                    score -= 20
                    issues.append(f"Only {test_functions} test functions found")
                
                # Check for assertions
                assertion_count = tests.count('assert ')
                if assertion_count == 0:
                    score -= 30
                    issues.append("No assertions found")
                elif assertion_count < test_functions:
                    score -= 15
                    issues.append("Some test functions lack assertions")
                
                # Check for edge case testing
                if "none" not in tests.lower() and "null" not in tests.lower():
                    score -= 10
                    issues.append("No null/None testing found")
                
                # Check for error testing
                if "exception" not in tests.lower() and "error" not in tests.lower():
                    score -= 10
                    issues.append("No error/exception testing found")
                
        except Exception as e:
            score -= 20
            issues.append(f"Test analysis error: {e}")
        
        return max(0, score)
    
    def _assess_security(self, code: str, language: str) -> float:
        """Assess security (0-100)."""
        score = 100.0
        issues = []
        
        # Security risk patterns
        security_risks = [
            "eval(", "exec(", "__import__", "input(", "raw_input(",
            "os.system(", "subprocess.call(", "subprocess.Popen(",
            "pickle.loads(", "marshal.loads(", "yaml.load(",
            "sqlite3.connect(", "mysql.connector.connect(",
            "password", "secret", "key", "token"
        ]
        
        for risk in security_risks:
            if risk in code.lower():
                score -= 15
                issues.append(f"Security risk: {risk}")
        
        # Check for hardcoded credentials
        if re.search(r'password\s*=\s*["\'][^"\']+["\']', code, re.IGNORECASE):
            score -= 25
            issues.append("Hardcoded password detected")
        
        if re.search(r'api_key\s*=\s*["\'][^"\']+["\']', code, re.IGNORECASE):
            score -= 25
            issues.append("Hardcoded API key detected")
        
        # Check for SQL injection risks
        if "sql" in code.lower() and "?" not in code and "%s" not in code:
            score -= 20
            issues.append("Potential SQL injection risk")
        
        # Check for input validation
        if "input(" in code.lower() and "validate" not in code.lower():
            score -= 15
            issues.append("Input validation missing")
        
        return max(0, score)
    
    def _assess_performance(self, code: str, language: str) -> float:
        """Assess performance (0-100)."""
        score = 100.0
        issues = []
        
        # Performance anti-patterns
        performance_issues = [
            "for.*for",  # Nested loops
            "while.*while",  # Nested while loops
            "time.sleep(",  # Blocking sleep
            "threading.sleep(",
            "requests.get(",  # Synchronous HTTP calls
            "urllib.request.urlopen(",
            "open(",  # File operations without context managers
            "file(",
        ]
        
        for pattern in performance_issues:
            if re.search(pattern, code, re.IGNORECASE):
                score -= 10
                issues.append(f"Performance issue: {pattern}")
        
        # Check for memory leaks
        if "global " in code and "del " not in code:
            score -= 5
            issues.append("Potential memory leak with global variables")
        
        # Check for efficient data structures
        if "list(" in code and "set(" not in code:
            score -= 5
            issues.append("Consider using sets for unique collections")
        
        return max(0, score)
    
    def _assess_documentation(self, code: str, language: str) -> float:
        """Assess documentation (0-100)."""
        score = 100.0
        issues = []
        
        # Check for module docstring
        if not code.strip().startswith('"""') and not code.strip().startswith("'''"):
            score -= 20
            issues.append("No module docstring found")
        
        # Check for function/class docstrings
        function_count = len(re.findall(r'def ', code))
        class_count = len(re.findall(r'class ', code))
        docstring_count = len(re.findall(r'"""', code)) + len(re.findall(r"'''", code))
        
        expected_docstrings = function_count + class_count + 1  # +1 for module docstring
        if docstring_count < expected_docstrings:
            score -= 30
            issues.append(f"Insufficient docstrings: {docstring_count}/{expected_docstrings}")
        
        # Check for inline comments
        comment_lines = len([line for line in code.split('\n') if line.strip().startswith('#')])
        code_lines = len([line for line in code.split('\n') if line.strip() and not line.strip().startswith('#')])
        
        if code_lines > 0 and comment_lines / code_lines < 0.1:
            score -= 15
            issues.append("Insufficient inline comments")
        
        # Check for README or requirements
        if "requirements" not in code.lower() and "dependencies" not in code.lower():
            score -= 10
            issues.append("No dependency information found")
        
        return max(0, score)
    
    def _identify_issues(self, scores: Dict[str, float]) -> List[str]:
        """Identify specific issues based on scores."""
        issues = []
        
        for category, score in scores.items():
            if score < 50:
                issues.append(f"Critical {category} issues (score: {score})")
            elif score < 70:
                issues.append(f"Moderate {category} issues (score: {score})")
            elif score < 85:
                issues.append(f"Minor {category} issues (score: {score})")
        
        return issues
    
    def _generate_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Generate recommendations based on scores."""
        recommendations = []
        
        if scores["code_quality"] < 70:
            recommendations.extend([
                "Add proper error handling with try-except blocks",
                "Include logging configuration",
                "Add docstrings to functions and classes",
                "Follow PEP 8 style guidelines"
            ])
        
        if scores["test_coverage"] < 70:
            recommendations.extend([
                "Add more unit tests",
                "Include edge case testing",
                "Add integration tests",
                "Test error scenarios"
            ])
        
        if scores["security"] < 70:
            recommendations.extend([
                "Remove hardcoded credentials",
                "Add input validation",
                "Use parameterized queries for database operations",
                "Implement proper authentication"
            ])
        
        if scores["performance"] < 70:
            recommendations.extend([
                "Optimize nested loops",
                "Use async/await for I/O operations",
                "Implement caching where appropriate",
                "Use efficient data structures"
            ])
        
        if scores["documentation"] < 70:
            recommendations.extend([
                "Add comprehensive docstrings",
                "Include inline comments",
                "Create README file",
                "Document dependencies and setup"
            ])
        
        return list(set(recommendations))  # Remove duplicates
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level based on overall score."""
        if score >= 90:
            return "low"
        elif score >= 70:
            return "medium"
        else:
            return "high"
    
    def _estimate_fix_time(self, issues: List[str]) -> str:
        """Estimate time to fix issues."""
        if not issues:
            return "0 hours"
        
        # Rough estimation: 2 hours per critical issue, 1 hour per moderate, 0.5 hours per minor
        critical_count = len([i for i in issues if "Critical" in i])
        moderate_count = len([i for i in issues if "Moderate" in i])
        minor_count = len([i for i in issues if "Minor" in i])
        
        total_hours = critical_count * 2 + moderate_count * 1 + minor_count * 0.5
        
        if total_hours < 1:
            return "Less than 1 hour"
        elif total_hours < 8:
            return f"{total_hours:.1f} hours"
        else:
            days = total_hours / 8
            return f"{days:.1f} days"
    
    def generate_deployment_report(self, assessment: Dict[str, Any]) -> str:
        """Generate a detailed deployment report."""
        report = f"""
# Deployment Readiness Assessment Report

## Overall Assessment
- **Ready for Deployment**: {'✅ Yes' if assessment['ready_for_deployment'] else '❌ No'}
- **Overall Score**: {assessment['overall_score']}/100
- **Risk Level**: {assessment['risk_level'].upper()}
- **Estimated Fix Time**: {assessment['estimated_fix_time']}

## Detailed Scores
"""
        
        for category, score in assessment['detailed_scores'].items():
            status = "✅" if score >= 70 else "⚠️" if score >= 50 else "❌"
            report += f"- **{category.replace('_', ' ').title()}**: {status} {score}/100\n"
        
        if assessment['issues']:
            report += "\n## Issues Found\n"
            for issue in assessment['issues']:
                report += f"- {issue}\n"
        
        if assessment['recommendations']:
            report += "\n## Recommendations\n"
            for rec in assessment['recommendations']:
                report += f"- {rec}\n"
        
        return report 