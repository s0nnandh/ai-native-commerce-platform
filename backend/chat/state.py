"""
ChatState and data models for the conversational store orchestration.
"""
from typing import Literal, Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator
from typing import Annotated
from langchain.schema import Document
from utils.product import Product
from langgraph.graph import add_messages
from enum import Enum
import json

class Citation(BaseModel):
    """Citation for informational responses."""
    id: str
    snippet: str

class SearchQuery(BaseModel):
    """
    Search query along with metadata filters to be passed for retrieval layer
    """
    query: str = Field(description="Search query to retrieve relevant products based on user request.")
    metadata_filters: Optional[Dict[str, Union[str, List[str]]]] = Field(
        description="Metadata filters to refine the search results",
        examples=[
            {"category": "serum", "skin_concern": "acne", "price_cap": 40.0},
            {"avoid_ingredients": ["fragrance", "alcohol"], "target_sku": "Vitamin C Brightening Serum"}
        ]
    )

    @field_validator('metadata_filters', mode='before')
    @classmethod
    def parse_metadata_filters(cls, v):
        """Parse JSON string to dict if needed"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return v


class FollowupUser(BaseModel):
    """Followup question for the user."""
    followup_question: str = Field(
        description="Followup question to ask the user to clarify their request.",
        examples=["What are your main concerns?", "What is your skin type?"]
    )

class FollowupRequired(str, Enum):
    YES = "yes"
    NO = "no"

class ClassifyAndExtractUserIntent(BaseModel):
    """Classify and extract intent and constraints."""
    intent: Literal["RECOMMEND_SPECIFIC", "RECOMMEND_VAGUE", "INFO_PRODUCT", 
                "INFO_GENERAL", "OTHER"] = Field(
                    description="Classifies the type of user request - specific product recommendation, vague recommendation, followup to previous question, general information, product overview, or other",
                    examples=["RECOMMEND_SPECIFIC", "RECOMMEND_VAGUE", "INFO_PRODUCT"]
                )
    ask_followup: FollowupRequired = Field(
        default="no",
        description="Whether a follow-up question is needed: 'yes' or 'no'",
        examples=["yes", "no"]
    ),
    followup_topics: Optional[List[Literal["name", "product_id", "concerns", "category", "keywords", "avoid_ingredients", "other", "price", "top_ingredients"]]] = Field(
        default=[],
        description="List of follow-up topics if ask_followup is True, depending on user history",
        examples=[["category", "product_id", "concern"]]
    )
    category: Optional[List[Literal["serum", "toner", 
                        "sunscreen", "moisturizer", 
                        "face_mask", "body_wash",
                            "shampoo", "conditioner", 
                            "hair_mask"]]] = Field(
                                default=[],
                                description="Product categories mentioned or implied in the user request. Multiple categories can be specified.",
                                examples=[["serum"], ["moisturizer", "sunscreen"], ["toner"]]
                            )
    name: Optional[List[str]] = Field(
        default=[],
        description="Specific product names mentioned by the user. Can include partial or full product names.",
        examples=[["Vitamin C Brightening Serum"], ["Hydrating Toner"], ["Ultra Moisturizer"]]
    )
    top_ingredients: Optional[List[str]] = Field(
        default=[],
        description="Key ingredients mentioned by the user, either desired or discussed. Includes active ingredients and notable formulation components.",
        examples=[["hyaluronic acid", "vitamin C"], ["retinol"], ["niacinamide", "ceramides"]]
    )  
    concerns: Optional[List[str]] = Field(
        default=[],
        description="Skin, hair, face, body concerns mentioned by the user.",
        examples=[["acne", "oiliness"], ["dryness"], ["aging", "fine lines"], ["sensitivity"]]
    )
    keywords: Optional[List[str]] = Field(
        default=[],
        description="User-specific characteristics, preferences, and concerns such as skin types (oily, dry, sensitive), skin conditions (acne-prone, aging, redness), hair types (dyed, curly, thin), texture preferences (gel, cream, lightweight), and sensory preferences (fragrance-free, cooling)",
        examples=[["oily skin", "acne-prone"], ["dyed-hair", "damaged"], ["sensitive", "redness"], ["lightweight", "gel texture"]]
    )
    avoid_ingredients: Optional[List[str]] = Field(
        default=[],
        description="Ingredients mentioned by the user that should be avoided in the recommendations.",
        examples=[["fragrance", "alcohol"], ["parabens"], ["sulfates", "silicones"]]
    )
    product_id: Optional[List[str]] = Field(
        default=[],
        description="Specific product IDs mentioned by the user. Can include partial or full product IDs.",
        examples=[["SKU123"], ["P12345"]]
    )
    price: Optional[List[str]] = Field(
        default=[],
        description="Price range mentioned by the user, in USD.",
        examples=[["under $40"], ["$20-30"], ["budget-friendly"]]
    )
    other: Optional[List[str]] = Field(
        default=[],
        description="Any other important information that can be extracted from the user's message like finish of the product eg: matte",
        examples=[["matte finish"], ["travel size"], ["cruelty-free"], ["vegan"]]
    )

    @field_validator('intent')
    @classmethod
    def validate_intent(cls, v):
        """Validate intent enum values."""
        if v is not None:
            allowed_intents = {"RECOMMEND_SPECIFIC", "RECOMMEND_VAGUE", "INFO_PRODUCT", "INFO_GENERAL", "OTHER"}
            if v not in allowed_intents:
                raise ValueError(f"Intent must be one of {allowed_intents}, got {v}")
        return v
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        """Validate category enum values."""
        if v is not None:
            allowed_categories = {"serum", "toner", "sunscreen", "moisturizer", "face_mask", "body_wash", "shampoo", "conditioner", "hair_mask"}
            for category in v:
                if category not in allowed_categories:
                    raise ValueError(f"Category must be one of {allowed_categories}, got {category}")
        return v

class ChatState(BaseModel):
    """
    State object for LangGraph conversation orchestration.
    Tracks conversation context, constraints, and generated outputs.
    """
    session_id: str
    turn_count: int = 0
    
    # messages 
    user_messages: List[str] = Field(default_factory=list)  
    ai_messages: List[str] = Field(default_factory=list)


    intent: str = None
    extracted_info: ClassifyAndExtractUserIntent = None

    followup_topics: List[str] = Field(default_factory=list)
    ask_followup: FollowupRequired = Field(default="no")

    # priority order of keys
    missing_keys: List[str] = Field(default_factory=list)
    
    # Retrieval and outputs
    retrieved_docs: List[Document] = Field(default_factory=list)
    products: List[Product] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    
    # def merge_constraints(self, new_constraints: Dict[str, Any]) -> None:
    #     """
    #     Merge new constraints into existing ones, handling list merging appropriately.
    #     """
    #     for key, value in new_constraints.items():
    #         if key in ['avoid_ingredients', 'desired_ingredients']:
    #             # Merge lists, avoiding duplicates
    #             existing = self.constraints.get(key, [])
    #             if isinstance(existing, list) and isinstance(value, list):
    #                 merged = list(set(existing + value))
    #                 self.constraints[key] = merged
    #             else:
    #                 self.constraints[key] = value if isinstance(value, list) else [value]
    #         else:
    #             # Direct assignment for non-list constraints
    #             self.constraints[key] = value
    
    def get_constraint_priority_order(self) -> List[str]:
        """
        Return constraint keys in priority order for followup questions.
        Safety-first approach with critical constraints prioritized.
        """
        return [
            'category',
            'concerns',
            'keywords',          
            'name',
            'product_id',
            'avoid_ingredients',
            'top_ingredients', 
            'price',          
            'other'             
        ]
    
    def get_constraint_groups(self) -> Dict[str, List[str]]:
        """
        Group constraints by criticality for smarter followup logic.
        """
        return {
            'SPECIFIC_CONSTRAINTS': ['name', 'product_id'],
            'CRITICAL_CONSTRAINTS': ['category', 'concerns'],
            'IMPORTANT_CONSTRAINTS': ['keywords', 'avoid_ingredients', 'top_ingredients'],
            'NICE_TO_HAVE': ['price', 'other']
        }
    
    def should_ask_followup(self) -> tuple[bool, List[str]]:
        """
        Determine if we should ask a followup question based on:
        1. Turn count (max 3 turns total)
        2. Constraint criticality
        3. Information completeness
        
        Returns:
            Tuple of (should_ask_followup, list_of_followup_keys)
        """
        # Never ask after 3 turns
        if self.turn_count >= 3:
            return False, []

        # If specific constraints are added, do not follow up 
        if self.extracted_info and self.extracted_info.intent == "RECOMMEND_SPECIFIC":
            return False, []
        
        # if any of the critical constraints are missing, follow up 
        critical_constraints = self.get_constraint_groups()['CRITICAL_CONSTRAINTS']
        missing_critical = [key for key in critical_constraints if key in self.missing_keys]
        if missing_critical:
            return True, missing_critical
        
        # if it is the first turn and any of the important constraints are missing, follow up
        if self.turn_count == 0:
            important_constraints = self.get_constraint_groups()['IMPORTANT_CONSTRAINTS']
            missing_important = [key for key in important_constraints if key in self.missing_keys]
            if missing_important:
                return True, missing_important
        
        return False, []
    
    def reset_for_new_turn(self) -> None:
        """Reset state for a new conversation turn while preserving session context."""
        # Save messages to history lists before clearing
        if self.user_message:
            self.user_messages_list.append(self.user_message)
        if self.ai_message:
            self.ai_messages_list.append(self.ai_message)
            
        # Reset current message state
        self.user_message = None
        self.ai_message = None
        
        # Reset other state for new turn
        self.ask_followup = "no"
        self.followup_keys = []
        self.retrieved_docs = []
        self.products = []
        self.citations = []


class IntentClassificationResult(BaseModel):
    """Result from business-focused intent classification LLM call."""
    intent: Literal["RECOMMEND_SPECIFIC", "RECOMMEND_VAGUE", "FOLLOWUP_ANSWER", "INFORMATIONAL", "OVERVIEW", "OTHER"]
    ask_followup: bool
    followup_question: Optional[str] = None
    detected_constraints: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('intent')
    @classmethod
    def validate_intent_enum(cls, v):
        """Validate business intent enum values."""
        allowed_intents = {"RECOMMEND_SPECIFIC", "RECOMMEND_VAGUE", "FOLLOWUP_ANSWER", "INFORMATIONAL", "OVERVIEW", "OTHER"}
        if v not in allowed_intents:
            raise ValueError(f"Intent must be one of {allowed_intents}, got {v}")
        return v


class AssistResponse(BaseModel):
    """Response format for the /api/assist endpoint."""
    text: str
    ask_followup: bool
    followup_keys: List[str] = Field(default_factory=list)
    products: List[Dict[str, Any]] = Field(default_factory=list)
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    latency_ms: int