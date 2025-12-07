"""
Comprehensive Tool Testing Suite
Tests all AutoGen tools end-to-end
"""

import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from tools import (
    search_web,
    brave_search,
    get_stock_data,
    get_weather,
    execute_python_code,
    save_to_file
)

load_dotenv()

print("\n" + "="*80)
print("AUTOGEN TOOLS - COMPREHENSIVE END-TO-END TEST")
print("="*80 + "\n")

# Test 1: Serper Web Search
print("[1/6] Testing Serper Web Search...")
print("-" * 80)
result = search_web("artificial intelligence 2024")
print(f"Status: {'✅ SUCCESS' if result.get('count', 0) > 0 else '❌ FAILED'}")
print(f"Results count: {result.get('count', 0)}")
if result.get('error'):
    print(f"Error: {result['error']}")
if result.get('results'):
    print(f"Sample result: {result['results'][0].get('title', 'N/A')}")
print()

# Test 2: Brave Search
print("[2/6] Testing Brave Search...")
print("-" * 80)
result = brave_search("machine learning trends")
print(f"Status: {'✅ SUCCESS' if result.get('count', 0) > 0 else '❌ FAILED'}")
print(f"Results count: {result.get('count', 0)}")
if result.get('error'):
    print(f"Error: {result['error']}")
if result.get('results'):
    print(f"Sample result: {result['results'][0].get('title', 'N/A')}")
print()

# Test 3: Alpha Vantage Stock Data
print("[3/6] Testing Alpha Vantage Stock Data...")
print("-" * 80)
result = get_stock_data("AAPL")
print(f"Status: {'✅ SUCCESS' if 'symbol' in result else '❌ FAILED'}")
if result.get('error'):
    print(f"Error: {result['error']}")
else:
    print(f"Symbol: {result.get('symbol', 'N/A')}")
    print(f"Price: ${result.get('price', 'N/A')}")
    print(f"Change: {result.get('change', 'N/A')} ({result.get('change_percent', 'N/A')})")
print()

# Test 4: OpenWeather
print("[4/6] Testing OpenWeather API...")
print("-" * 80)
result = get_weather("New York")
print(f"Status: {'✅ SUCCESS' if 'city' in result else '❌ FAILED'}")
if result.get('error'):
    print(f"Error: {result['error']}")
else:
    print(f"City: {result.get('city', 'N/A')}")
    print(f"Temperature: {result.get('temperature', 'N/A')}")
    print(f"Description: {result.get('description', 'N/A')}")
    print(f"Humidity: {result.get('humidity', 'N/A')}")
print()

# Test 5: Python Code Execution
print("[5/6] Testing Python Code Execution...")
print("-" * 80)
test_code = """
import numpy as np
arr = np.array([1, 2, 3, 4, 5])
print(f"Array: {arr}")
print(f"Mean: {np.mean(arr)}")
print(f"Sum: {np.sum(arr)}")
"""
result = execute_python_code(test_code)
print(f"Status: {'✅ SUCCESS' if result.get('success') else '❌ FAILED'}")
if result.get('success'):
    print(f"Output:\n{result.get('stdout', '')}")
else:
    print(f"Error: {result.get('error', 'Unknown error')}")
    print(f"Stderr: {result.get('stderr', '')}")
print()

# Test 6: File Management
print("[6/6] Testing File Save...")
print("-" * 80)
result = save_to_file("test_output.txt", "AutoGen tool test successful!")
print(f"Status: {'✅ SUCCESS' if result.get('status') == 'success' else '❌ FAILED'}")
if result.get('status') == 'success':
    print(f"File saved to: {result.get('filepath')}")
else:
    print(f"Error: {result.get('message')}")
print()

# Summary
print("="*80)
print("TEST SUMMARY")
print("="*80)
print("Tools tested: 6")
print("Check results above for detailed status of each tool")
print()
