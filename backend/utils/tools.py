"""
Tools for LLM function calling in the conversational store.
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from langchain_core.tools import tool


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
def classify_user_intent(
    intent: Literal[
        "RECOMMEND_SPECIFIC", 
        "RECOMMEND_VAGUE", 
        "FOLLOWUP_ANSWER", 
        "INFORMATIONAL", 
        "OVERVIEW", 
        "OTHER"
    ],
    category: Optional[str] = None,
    skin_concern: Optional[str] = None,
    avoid_ingredients: Optional[List[str]] = None,
    desired_ingredients: Optional[List[str]] = None,
    price_cap: Optional[float] = None,
    target_sku: Optional[str] = None,
    finish: Optional[str] = None,
    ask_followup: bool = False,
    followup_question: Optional[str] = None,
    confidence_score: Optional[float] = None
) -> str:
    """
    Classify user intent and extract skincare product constraints.
    
    Intent Categories with Business Logic:
    
    RECOMMEND_SPECIFIC: User has enough info (category + 1-2 details)
    - "Vitamin C serum under $40" 
    - "Hydrating toner for acne-prone skin"
    - Set ask_followup = False
    
    RECOMMEND_VAGUE: User wants products but needs clarification
    - "Something gentle for summer"
    - "Looking for skincare gifts" 
    - Set ask_followup = True if missing critical info
    
    FOLLOWUP_ANSWER: Direct response to previous question
    - "My skin is oily", "Under $30 please"
    - Set ask_followup = False (NEVER ask new questions)
    
    INFORMATIONAL: Questions about products/ingredients
    - "Is retinol safe during pregnancy?"
    - Set ask_followup = True if missing important/critical info
    
    OVERVIEW: Company/policy questions
    - "What's your return policy?"
    - Set ask_followup = False
    
    OTHER: Greetings, thanks, off-topic
    - "Hi there!", "Thank you!"
    - Set ask_followup = False
    
    Constraint Extraction:
    - category: cleanser, serum, moisturizer, toner, mask, sunscreen
    - skin_concern: acne, dryness, aging, sensitivity, oiliness
    - avoid_ingredients: fragrance, alcohol, parabens, sulfates
    - desired_ingredients: hyaluronic acid, vitamin C, retinol, niacinamide
    - price_cap: numerical budget (e.g. 40.0 for "under $40")
    - target_sku: specific product names mentioned
    - finish: matte, dewy, lightweight, rich, gel, cream
    
    Args:
        intent: The classified intent category
        category: Product category if mentioned
        skin_concern: Primary skin concern if mentioned
        avoid_ingredients: List of ingredients to avoid
        desired_ingredients: List of preferred ingredients
        price_cap: Maximum budget in USD
        target_sku: Specific product name or SKU
        finish: Texture/finish preference
        ask_followup: Whether to ask a follow-up question
        followup_question: The follow-up question if ask_followup is True
        confidence_score: Confidence in classification (0.0-1.0)
    
    Returns:
        Dictionary with classification results and extracted constraints
    """
    # Build detected constraints dict, filtering out None/empty values
    return "Detecting constraints and intent"
    
    # return {
    #     "intent": intent,
    #     "ask_followup": ask_followup,
    #     "constraints": detected_constraints,
    #     "followup_question": followup_question,
    #     "confidence_score": confidence_score
    # }


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
        return [classify_user_intent]
    
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