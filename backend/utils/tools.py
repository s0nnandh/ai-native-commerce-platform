"""
Tools for LLM function calling in the conversational store.
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from langchain_core.tools import tool

from utils.constants import IntentConfig, COMMON_SKIN_CONCERNS, VALID_CATEGORIES


class DetectedConstraints(BaseModel):
    """Structured constraints detected from user message."""
    category: Optional[str] = Field(
        None, 
        description="Product category (cleanser, serum, moisturizer, etc.)"
    )
    skin_concern: Optional[str] = Field(
        None,
        description="Primary skin concern (acne, dryness, aging, etc.)"
    )
    avoid_ingredients: List[str] = Field(
        default_factory=list,
        description="Ingredients to avoid due to allergies or preferences"
    )
    desired_ingredients: List[str] = Field(
        default_factory=list,
        description="Preferred or desired ingredients"
    )
    price_cap: Optional[float] = Field(
        None,
        description="Maximum price budget in USD"
    )
    target_sku: Optional[str] = Field(
        None,
        description="Specific product name or SKU mentioned"
    )
    finish: Optional[str] = Field(
        None,
        description="Texture or finish preference (matte, dewy, lightweight, etc.)"
    )


@tool
def classify_intent_and_extract_constraints(
    intent: Literal["informational", "specific", "vague", "followup_answered"],
    ask_followup: bool,
    detected_constraints: DetectedConstraints,
    followup_question: Optional[str] = None,
    confidence_score: Optional[float] = None
) -> Dict[str, Any]:
    """
    Classify the user's intent and extract skincare product constraints.
    
    Args:
        intent: The classified intent of the user message
            - informational: User asking for information/advice about products
            - specific: User has clear product requirements
            - vague: User query needs clarification
            - followup_answered: User responding to a previous question
            
        ask_followup: Whether a follow-up question should be asked to clarify requirements
        
        detected_constraints: Structured constraints extracted from the message
        
        followup_question: Optional follow-up question if ask_followup is True
        
        confidence_score: Optional confidence in the classification (0.0-1.0)
    
    Returns:
        Dictionary containing the classification results
    """
    return {
        "intent": intent,
        "ask_followup": ask_followup,
        "detected_constraints": detected_constraints.dict(),
        "followup_question": followup_question,
        "confidence_score": confidence_score
    }


@tool  
def extract_product_preferences(
    categories: List[str] = Field(default_factory=list, description="Product categories of interest"),
    skin_type: Optional[str] = Field(None, description="User's skin type"),
    primary_concerns: List[str] = Field(default_factory=list, description="Primary skin concerns"),
    ingredient_preferences: List[str] = Field(default_factory=list, description="Preferred ingredients"),
    ingredient_restrictions: List[str] = Field(default_factory=list, description="Ingredients to avoid"),
    budget_range: Optional[str] = Field(None, description="Budget range (e.g., 'under $50', '$20-40')"),
    routine_step: Optional[str] = Field(None, description="Which step in skincare routine"),
    texture_preference: Optional[str] = Field(None, description="Preferred texture or finish")
) -> Dict[str, Any]:
    """
    Extract detailed product preferences from user message.
    Alternative tool for more granular preference extraction.
    
    Returns:
        Dictionary containing structured preferences
    """
    return {
        "categories": categories,
        "skin_type": skin_type, 
        "primary_concerns": primary_concerns,
        "ingredient_preferences": ingredient_preferences,
        "ingredient_restrictions": ingredient_restrictions,
        "budget_range": budget_range,
        "routine_step": routine_step,
        "texture_preference": texture_preference
    }


class ToolManager:
    """Manages tool binding and execution for different LLM operations."""
    
    @staticmethod
    def get_intent_classification_tools() -> List:
        """Get tools for intent classification."""
        return [classify_intent_and_extract_constraints]
    
    @staticmethod
    def get_preference_extraction_tools() -> List:
        """Get tools for detailed preference extraction."""
        return [extract_product_preferences]
    
    @staticmethod
    def bind_classification_tools(llm):
        """Bind intent classification tools to an LLM."""
        tools = ToolManager.get_intent_classification_tools()
        return llm.bind_tools(tools)
    
    @staticmethod
    def bind_preference_tools(llm):
        """Bind preference extraction tools to an LLM.""" 
        tools = ToolManager.get_preference_extraction_tools()
        return llm.bind_tools(tools)