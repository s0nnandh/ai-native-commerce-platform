"""
Simple request validation for the Flask API.
"""
from typing import Dict, Any, Tuple


class ValidationError(Exception):
    """Simple validation error exception."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def validate_assist_request(data: Dict[str, Any]) -> Tuple[str, str]:
    """
    Validate /api/assist request with basic checks.
    
    Args:
        data: Request JSON data
        
    Returns:
        Tuple of (session_id, user_message)
        
    Raises:
        ValidationError: If validation fails
    """
    if not data:
        raise ValidationError("Request body is required")
    
    # Validate session_id
    session_id = data.get('session_id', '').strip()
    if not session_id:
        raise ValidationError("session_id is required")
    
    if len(session_id) < 8:
        raise ValidationError("session_id must be at least 8 characters")
    
    # Validate message
    message = data.get('message', '').strip()
    if not message:
        raise ValidationError("message is required")
    
    if len(message) > 2000:
        raise ValidationError("message must be less than 2000 characters")
    
    return session_id, message