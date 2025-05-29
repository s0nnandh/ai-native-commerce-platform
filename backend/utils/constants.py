"""
Constants and configuration for the conversational store application.
"""
from typing import Dict, List

# LLM Configuration
class LLMConfig:
    """LLM model configurations and settings."""
    
    # Model names
    GPT_4_O_MINI_MODEL = "gpt-4o-mini"
    GEMINI_2_0_FLASH_MODEL = "gemini-2.0-flash"
    
    # Temperature settings
    CLASSIFICATION_TEMPERATURE = 0  # Deterministic for intent classification
    GENERATION_TEMPERATURE = 0.3   # Slightly creative for response generation
    
    # Token limits
    MAX_TOKENS_CLASSIFICATION = 500
    MAX_TOKENS_FOLLOWUP = 200
    MAX_TOKENS_RECOMMENDATION = 300
    MAX_TOKENS_INFORMATIONAL = 400


# Conversation Flow Constants
class ConversationConfig:
    """Configuration for conversation flow and constraints."""
    
    # Turn limits
    MAX_TURNS = 3
    MAX_FOLLOWUP_TURNS = 2
    
    # Constraint priorities and groupings
    CONSTRAINT_PRIORITY_ORDER = [
        'category',
        'skin_concern',
        'avoid_ingredients',
        'target_sku',
        'desired_ingredients',
        'price_cap',
        'finish'
    ]
    
    CRITICAL_CONSTRAINTS = ['category']
    IMPORTANT_CONSTRAINTS = ['skin_concern', 'avoid_ingredients', 'target_sku']  
    NICE_TO_HAVE_CONSTRAINTS = ['desired_ingredients', 'price_cap', 'finish']
    
    # Minimum info threshold for stopping followup questions
    MIN_CONSTRAINTS_FOR_RECOMMENDATION = 2


# Retrieval Configuration  
class RetrievalConfig:
    """Configuration for vector search and product retrieval."""
    
    # Vector search parameters
    DEFAULT_SIMILARITY_K = 25
    MAX_SIMILARITY_K = 50
    MIN_SIMILARITY_SCORE = 0.3
    SIMILARITY_SCORE=0.5
    
    # Product ranking
    TOP_PRODUCTS_FOR_RECOMMENDATION = 3
    MAX_PRODUCTS_TO_RANK = 100
    
    # Citation limits
    MAX_CITATIONS = 5
    MAX_SNIPPET_LENGTH = 200


# Response Generation Configuration
class ResponseConfig:
    """Configuration for AI response generation."""
    
    # Response length limits (ULTRA CONCISE)
    MAX_RECOMMENDATION_WORDS = 15   # ~12-15 words max
    MAX_INFORMATIONAL_WORDS = 15    # ~12-15 words max  
    MAX_FOLLOWUP_WORDS = 12         # ~10-12 words max
    
    # Response types
    RECOMMENDATION_MODE = "recommendation"
    INFORMATIONAL_MODE = "informational"
    FOLLOWUP_MODE = "followup"


# Error Messages and Fallbacks
class ErrorMessages:
    """Standard error messages and fallback responses."""
    
    CLASSIFICATION_FALLBACK = "I'd be happy to help you find the right skincare products. Could you tell me what you're looking for?"
    
    RETRIEVAL_ERROR = "I'm having trouble searching our products right now. Please try again in a moment."
    
    GENERATION_ERROR = "I encountered an issue generating your response. Please rephrase your question and try again."
    
    NO_PRODUCTS_FOUND = "I couldn't find products matching your criteria. Could you provide more details about what you're looking for?"
    
    GENERIC_ERROR = "I'm sorry, something went wrong. Please try again."