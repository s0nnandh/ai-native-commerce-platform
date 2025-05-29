#!/usr/bin/env python3
"""
Setup Test Script for AI-Native Commerce Platform

This script tests the basic functionality of the AI-Native Commerce Platform
to ensure that the environment is properly configured and the application
is working as expected.
"""

import os
import sys
import json
import requests
import time
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize colorama
init()

def print_header(message):
    """Print a formatted header message."""
    print(f"\n{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{message.center(80)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\n")

def print_success(message):
    """Print a success message."""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    """Print an error message."""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_warning(message):
    """Print a warning message."""
    print(f"{Fore.YELLOW}! {message}{Style.RESET_ALL}")

def print_info(message):
    """Print an info message."""
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")

def check_env_variables():
    """Check if required environment variables are set."""
    print_header("Checking Environment Variables")
    
    # Load environment variables from .env file
    load_dotenv()
    
    required_vars = ["OPENAI_API_KEY"]
    optional_vars = ["GEMINI_API_KEY", "GOOGLE_API_KEY", "LANGSMITH_API_KEY", 
                     "VITE_API_BASE_URL", "FLASK_ENV", "FLASK_DEBUG"]
    
    all_required_present = True
    
    # Check required variables
    for var in required_vars:
        if os.getenv(var):
            print_success(f"Required variable {var} is set")
        else:
            print_error(f"Required variable {var} is not set")
            all_required_present = False
    
    # Check optional variables
    for var in optional_vars:
        if os.getenv(var):
            print_success(f"Optional variable {var} is set")
        else:
            print_warning(f"Optional variable {var} is not set")
    
    return all_required_present

def check_backend_health(base_url="http://localhost:5000"):
    """Check if the backend is running and healthy."""
    print_header("Checking Backend Health")
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print_success(f"Backend is healthy: {response.json()}")
            return True
        else:
            print_error(f"Backend returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to connect to backend: {e}")
        print_info("Make sure the backend is running on http://localhost:5000")
        print_info("You can start it with: docker-compose up backend")
        return False

def check_products_api(base_url="http://localhost:5000"):
    """Check if the products API is working."""
    print_header("Checking Products API")
    
    try:
        response = requests.get(f"{base_url}/api/products", timeout=5)
        if response.status_code == 200:
            products = response.json().get("products", [])
            print_success(f"Products API returned {len(products)} products")
            if products:
                print_info(f"Sample product: {json.dumps(products[0], indent=2)}")
            return True
        else:
            print_error(f"Products API returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to connect to Products API: {e}")
        return False

def test_chat_api(base_url="http://localhost:5000"):
    """Test the chat API with a simple message."""
    print_header("Testing Chat API")
    
    try:
        payload = {
            "message": "What skincare products do you have?",
            "sessionId": f"test-{int(time.time())}"
        }
        
        print_info(f"Sending message: {payload['message']}")
        
        response = requests.post(
            f"{base_url}/api/assist",
            json=payload,
            timeout=30  # LLM calls can take time
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Chat API responded successfully")
            print_info(f"Response: {result.get('response', 'No response text')[:100]}...")
            return True
        else:
            print_error(f"Chat API returned status code {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to connect to Chat API: {e}")
        return False

def check_frontend_access(url="http://localhost:80"):
    """Check if the frontend is accessible."""
    print_header("Checking Frontend Access")
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print_success(f"Frontend is accessible at {url}")
            return True
        else:
            print_error(f"Frontend returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to connect to frontend: {e}")
        print_info("Make sure the frontend is running on http://localhost:80")
        print_info("You can start it with: docker-compose up frontend")
        return False

def main():
    """Main function to run all tests."""
    print_header("AI-Native Commerce Platform Setup Test")
    
    # Check environment variables
    env_ok = check_env_variables()
    if not env_ok:
        print_warning("Some required environment variables are missing.")
        print_info("Please check your .env file and set all required variables.")
    
    # Check backend health
    backend_ok = check_backend_health()
    
    # If backend is healthy, check APIs
    if backend_ok:
        products_ok = check_products_api()
        chat_ok = test_chat_api()
    else:
        products_ok = False
        chat_ok = False
        print_warning("Skipping API tests because backend is not healthy.")
    
    # Check frontend access
    frontend_ok = check_frontend_access()
    
    # Print summary
    print_header("Test Summary")
    print(f"Environment Variables: {'✓' if env_ok else '✗'}")
    print(f"Backend Health: {'✓' if backend_ok else '✗'}")
    print(f"Products API: {'✓' if products_ok else '✗'}")
    print(f"Chat API: {'✓' if chat_ok else '✗'}")
    print(f"Frontend Access: {'✓' if frontend_ok else '✗'}")
    
    # Print overall result
    if all([env_ok, backend_ok, products_ok, chat_ok, frontend_ok]):
        print_success("\nAll tests passed! Your setup is working correctly.")
    else:
        print_error("\nSome tests failed. Please check the errors above and fix them.")
        print_info("For more information, refer to the README.md file.")

if __name__ == "__main__":
    main()
