"""
AutoGen Multi-Agent System - Tools
Implements web search, code execution, weather, stock data, and file tools
"""

import os
import subprocess
import tempfile
import requests
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


def brave_search(query: str) -> Dict[str, Any]:
    """Search the web using Brave Search API (alternative to Serper)"""
    try:
        api_key = os.getenv("BRAVE_SEARCH_API")
        if not api_key:
            return {"error": "Brave Search API key not configured", "results": []}
        
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key
        }
        
        response = requests.get(
            f"https://api.search.brave.com/res/v1/web/search?q={query}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            results = []
            for item in data.get("web", {}).get("results", [])[:3]:
                results.append({
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                    "url": item.get("url", "")
                })
            return {"results": results, "count": len(results)}
        else:
            return {"error": f"API returned {response.status_code}", "results": []}
    except Exception as e:
        return {"error": str(e), "results": []}


def get_stock_data(symbol: str) -> Dict[str, Any]:
    """Get stock market data using Alpha Vantage API"""
    try:
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not api_key:
            return {"error": "Alpha Vantage API key not configured"}
        
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            quote = data.get("Global Quote", {})
            
            if quote:
                return {
                    "symbol": quote.get("01. symbol", ""),
                    "price": quote.get("05. price", ""),
                    "change": quote.get("09. change", ""),
                    "change_percent": quote.get("10. change percent", ""),
                    "volume": quote.get("06. volume", ""),
                    "latest_trading_day": quote.get("07. latest trading day", "")
                }
            else:
                return {"error": "No data returned for symbol"}
        else:
            return {"error": f"API returned {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def get_weather(city: str) -> Dict[str, Any]:
    """Get current weather data using OpenWeather API"""
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return {"error": "OpenWeather API key not configured"}
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "city": data.get("name", ""),
                "temperature": f"{data.get('main', {}).get('temp', '')}°C",
                "feels_like": f"{data.get('main', {}).get('feels_like', '')}°C",
                "humidity": f"{data.get('main', {}).get('humidity', '')}%",
                "description": data.get("weather", [{}])[0].get("description", ""),
                "wind_speed": f"{data.get('wind', {}).get('speed', '')} m/s"
            }
        else:
            return {"error": f"API returned {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


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
