"""
File Manager utility for handling file operations.
"""

import os
import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

class FileManager:
    """Manages file operations for generated code, tests, and other artifacts."""
    
    def __init__(self, base_dir: str = "generated"):
        self.base_dir = Path(base_dir)
        self.code_dir = self.base_dir / "code"
        self.test_dir = self.base_dir / "tests"
        self.assessment_dir = self.base_dir / "assessments"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all necessary directories exist."""
        for directory in [self.base_dir, self.code_dir, self.test_dir, self.assessment_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _sanitize_filename(self, text: str, max_length: int = 100) -> str:
        """Sanitize text to create a valid filename."""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            text = text.replace(char, '_')
        
        # Replace spaces with underscores
        text = text.replace(' ', '_')
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove trailing underscores
        text = text.rstrip('_')
        
        return text
    
    def save_project_file(self, requirement: str, filename: str, content: str) -> str:
        """Save project file with proper extension based on filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_req = self._sanitize_filename(requirement[:50])
        
        # Determine the correct directory based on file type
        if filename.endswith(('.py', '.js', '.java', '.cpp', '.c', '.go', '.rs')):
            # Code files go to code directory
            directory = self.code_dir
        elif filename.startswith('test_') or filename.endswith('_test.py'):
            # Test files go to test directory
            directory = self.test_dir
        else:
            # Other files (config, docs, etc.) go to code directory
            directory = self.code_dir
        
        # Create the full filename with timestamp
        full_filename = f"{timestamp}_{sanitized_req}_{filename}"
        file_path = directory / full_filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path)
    
    def save_code_file(self, requirement: str, code: str) -> str:
        """Save generated code to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_req = self._sanitize_filename(requirement[:50])
        filename = f"{timestamp}_{sanitized_req}.py"
        file_path = self.code_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        return str(file_path)
    
    def save_test_file(self, requirement: str, test_code: str) -> str:
        """Save generated test code to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_req = self._sanitize_filename(requirement[:50])
        filename = f"test_{timestamp}_{sanitized_req}.py"
        file_path = self.test_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(test_code)
        
        return str(file_path)
    
    def save_assessment_file(self, requirement: str, assessment: Dict[str, Any]) -> str:
        """Save deployment assessment to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_req = self._sanitize_filename(requirement[:50])
        filename = f"assessment_{timestamp}_{sanitized_req}.json"
        file_path = self.assessment_dir / filename
        
        # Add metadata to assessment
        assessment_data = {
            "requirement": requirement,
            "timestamp": datetime.now().isoformat(),
            "assessment": assessment
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(assessment_data, f, indent=2, ensure_ascii=False)
        
        return str(file_path)
    
    def save_project_structure_file(self, requirement: str, project_structure: Dict[str, Any]) -> str:
        """Save project structure to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_req = self._sanitize_filename(requirement[:50])
        filename = f"project_structure_{timestamp}_{sanitized_req}.json"
        file_path = self.assessment_dir / filename
        
        # Add metadata to project structure
        structure_data = {
            "requirement": requirement,
            "timestamp": datetime.now().isoformat(),
            "project_structure": project_structure
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(structure_data, f, indent=2, ensure_ascii=False)
        
        return str(file_path)
    
    def list_generated_files(self) -> Dict[str, List[str]]:
        """List all generated files organized by type."""
        files = {
            "code": [],
            "tests": [],
            "assessments": []
        }
        
        # List code files
        for file_path in self.code_dir.glob("*.py"):
            files["code"].append(str(file_path))
        
        # List test files
        for file_path in self.test_dir.glob("*.py"):
            files["tests"].append(str(file_path))
        
        # List assessment files
        for file_path in self.assessment_dir.glob("*.json"):
            files["assessments"].append(str(file_path))
        
        return files
    
    def get_file_contents(self, file_path: str) -> str:
        """Get contents of a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def get_file_size(self, file_path: str) -> str:
        """Get human-readable file size."""
        try:
            size_bytes = os.path.getsize(file_path)
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        except Exception:
            return "Unknown"
    
    def create_zip_archive(self, file_list: List[Dict[str, Any]]) -> str:
        """Create a ZIP archive of all generated files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"generated_files_{timestamp}.zip"
        zip_path = self.base_dir / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_info in file_list:
                if os.path.exists(file_info['path']):
                    # Add file to zip with relative path
                    arcname = f"{file_info['type']}/{os.path.basename(file_info['path'])}"
                    zipf.write(file_info['path'], arcname)
        
        return str(zip_path)
    
    def cleanup_old_files(self, days_old: int = 7):
        """Clean up files older than specified days."""
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        
        for directory in [self.code_dir, self.test_dir, self.assessment_dir]:
            for file_path in directory.iterdir():
                if file_path.is_file():
                    file_time = file_path.stat().st_mtime
                    if file_time < cutoff_time:
                        try:
                            file_path.unlink()
                        except Exception as e:
                            print(f"Error deleting {file_path}: {e}")
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get detailed information about a file."""
        try:
            stat = os.stat(file_path)
            return {
                "name": os.path.basename(file_path),
                "path": file_path,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "type": self._get_file_type(file_path)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine file type based on extension and content."""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.py':
            if 'test_' in os.path.basename(file_path):
                return 'test'
            else:
                return 'code'
        elif ext == '.json':
            return 'assessment'
        else:
            return 'other' 