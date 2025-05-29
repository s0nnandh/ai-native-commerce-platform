"""
Simple error handling for the Flask API.
"""
import time
from typing import Dict, Any, Tuple
import structlog
from flask import jsonify
from utils.validation import ValidationError

logger = structlog.get_logger()


class APIError(Exception):
    """Simple API error exception."""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def handle_api_error(error: Exception, request_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Handle API errors and return JSON response.
    
    Args:
        error: The exception that occurred
        request_id: Request identifier
        
    Returns:
        Tuple of (json_response, status_code)
    """
    # Determine status code and message
    if isinstance(error, APIError):
        status_code = error.status_code
        message = error.message
    elif isinstance(error, ValidationError):
        status_code = 400
        message = str(error)
    else:
        status_code = 500
        message = "An internal error occurred"
    
    # Create response
    response = {
        "error": message,
        "request_id": request_id,
        "timestamp": time.time()
    }
    
    # Log the error
    logger.error("api_error",
                request_id=request_id,
                error_message=str(error),
                status_code=status_code)
    
    return jsonify(response), status_code


def create_fallback_response() -> Dict[str, Any]:
    """Create a fallback response when everything fails."""
    return {
        "text": "I'm experiencing technical difficulties. Please try again.",
        "ask_followup": "no",
        "followup_key": None,
        "products": [],
        "citations": [],
        "latency_ms": 0
    }