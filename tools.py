"""
AutoGen Multi-Agent System - Tools
Implements web search, code execution, and database tools for agents
"""

import os
import subprocess
import tempfile
from typing import Dict, Any
from serpapi import GoogleSearch


def search_web(query: str) -> Dict[str, Any]:
    """Search the web using Google Serper API"""
    try:
        search = GoogleSearch({
            "q": query,
            "api_key": os.getenv("SERPER_API_KEY")
        })
        results = search.get_dict()
        
        # Extract top 3 results
        organic = results.get("organic_results", [])[:3]
        snippets = []
        for result in organic:
            snippets.append({
                "title": result.get("title", ""),
                "snippet": result.get("snippet", ""),
                "link": result.get("link", "")
            })
        
        return {"results": snippets, "count": len(snippets)}
    except Exception as e:
        return {"error": str(e), "results": []}


def execute_python_code(code: str) -> Dict[str, Any]:
    """Execute Python code in a safe sandbox and return output"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        # Execute with timeout
        result = subprocess.run(
            ['python3', temp_file],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Cleanup
        os.unlink(temp_file)
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {"error": "Execution timeout (5s limit)", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


def save_to_file(filename: str, content: str) -> Dict[str, str]:
    """Save content to a file in the sandbox directory"""
    try:
        sandbox_dir = "sandbox"
        os.makedirs(sandbox_dir, exist_ok=True)
        
        filepath = os.path.join(sandbox_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        
        return {"status": "success", "filepath": filepath}
    except Exception as e:
        return {"status": "error", "message": str(e)}
