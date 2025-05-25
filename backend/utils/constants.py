"""
Constants and configuration for the conversational store application.
"""
from typing import Dict, List

# LLM Configuration
class LLMConfig:
    """LLM model configurations and settings."""
    
    # Model names
    GPT_3_5_MODEL = "gpt-3.5-turbo-1106"
    GEMINI_FLASH_MODEL = "gemini-1.5-flash-latest"
    
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
    
    CRITICAL_CONSTRAINTS = ['category', 'skin_concern']
    IMPORTANT_CONSTRAINTS = ['avoid_ingredients', 'target_sku']  
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
    
    # Product ranking
    TOP_PRODUCTS_FOR_RECOMMENDATION = 3
    MAX_PRODUCTS_TO_RANK = 100
    
    # Citation limits
    MAX_CITATIONS = 5
    MAX_SNIPPET_LENGTH = 200


# Response Generation Configuration
class ResponseConfig:
    """Configuration for AI response generation."""
    
    # Response length limits (in words)
    MAX_RECOMMENDATION_WORDS = 80
    MAX_INFORMATIONAL_WORDS = 80
    MAX_FOLLOWUP_WORDS = 30
    
    # Response types
    RECOMMENDATION_MODE = "recommendation"
    INFORMATIONAL_MODE = "informational"
    FOLLOWUP_MODE = "followup"


# Intent Classification Constants
class IntentConfig:
    """Configuration for intent classification."""
    
    VALID_INTENTS = {
        "informational",
        "specific", 
        "vague",
        "followup_answered"
    }
    
    # Intent descriptions for classification prompt
    INTENT_DESCRIPTIONS = {
        "informational": "User is asking for information about products, ingredients, or skincare advice",
        "specific": "User has specific product requirements and constraints",
        "vague": "User query is unclear or needs more information to provide good recommendations",
        "followup_answered": "User is responding to a previous follow-up question"
    }


# Error Messages and Fallbacks
class ErrorMessages:
    """Standard error messages and fallback responses."""
    
    CLASSIFICATION_FALLBACK = "I'd be happy to help you find the right skincare products. Could you tell me what you're looking for?"
    
    RETRIEVAL_ERROR = "I'm having trouble searching our products right now. Please try again in a moment."
    
    GENERATION_ERROR = "I encountered an issue generating your response. Please rephrase your question and try again."
    
    NO_PRODUCTS_FOUND = "I couldn't find products matching your criteria. Could you provide more details about what you're looking for?"
    
    GENERIC_ERROR = "I'm sorry, something went wrong. Please try again."


# Logging Configuration
class LoggingConfig:
    """Configuration for structured logging."""
    
    # Log levels for different operations
    LOG_LEVELS = {
        "entry": "info",
        "classification": "info", 
        "constraint_evaluation": "info",
        "retrieval": "info",
        "ranking": "info",
        "generation": "info",
        "error": "error"
    }
    
    # Fields to always include in logs
    STANDARD_LOG_FIELDS = [
        "session_id",
        "turn_count", 
        "timestamp",
        "latency_ms"
    ]


# Function Schema for OpenAI Function Calling
INTENT_CLASSIFICATION_FUNCTION_SCHEMA = {
    "name": "classify_intent",
    "description": "Classify user intent and extract constraints for skincare product search",
    "parameters": {
        "type": "object",
        "properties": {
            "intent": {
                "type": "string",
                "enum": list(IntentConfig.VALID_INTENTS),
                "description": "The classified intent of the user message"
            },
            "ask_followup": {
                "type": "boolean", 
                "description": "Whether a follow-up question should be asked"
            },
            "followup_question": {
                "type": "string",
                "description": "Optional follow-up question to ask the user"
            },
            "detected_constraints": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "skin_concern": {"type": "string"},
                    "avoid_ingredients": {"type": "array", "items": {"type": "string"}},
                    "desired_ingredients": {"type": "array", "items": {"type": "string"}},
                    "price_cap": {"type": "number"},
                    "target_sku": {"type": "string"},
                    "finish": {"type": "string"}
                },
                "description": "Extracted constraints from the user message"
            }
        },
        "required": ["intent", "ask_followup", "detected_constraints"]
    }
}


# Environment Configuration
class EnvironmentConfig:
    """Environment-specific configuration."""
    
    # API Keys (will be loaded from environment variables)
    OPENAI_API_KEY_ENV = "OPENAI_API_KEY"
    GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
    
    # Vector Store Configuration
    CHROMA_HOST_ENV = "CHROMA_HOST"
    CHROMA_PORT_ENV = "CHROMA_PORT"
    CHROMA_COLLECTION_NAME = "corpus"
    
    # Redis Configuration (for future use)
    REDIS_HOST_ENV = "REDIS_HOST"
    REDIS_PORT_ENV = "REDIS_PORT"
    REDIS_DB_ENV = "REDIS_DB"


# Constraint Mapping for Natural Language
CONSTRAINT_NATURAL_LANGUAGE_MAP = {
    "category": "product category",
    "skin_concern": "skin concern or goal", 
    "avoid_ingredients": "ingredients to avoid",
    "desired_ingredients": "preferred ingredients",
    "price_cap": "budget or price range",
    "target_sku": "specific product",
    "finish": "texture or finish preference"
}


# Product Categories (should match your catalog)
VALID_CATEGORIES = {
    "cleanser",
    "toner", 
    "serum",
    "moisturizer",
    "sunscreen",
    "treatment",
    "mask",
    "oil"
}


# Common Skin Concerns
COMMON_SKIN_CONCERNS = {
    "acne",
    "dryness", 
    "oily_skin",
    "sensitive_skin",
    "aging",
    "hyperpigmentation",
    "rosacea",
    "blackheads",
    "large_pores",
    "dullness"
}