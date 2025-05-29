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
            {"category": "serum", "skin_concern": "acne", "price_cap": "40.0"},
            {"avoid_ingredients": ["fragrance", "alcohol"], "product_name": "Vitamin C Brightening Serum"}
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
        default="yes",
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
                        "face-mask", "body-wash",
                            "shampoo", "conditioner", 
                            "hair-mask"]]] = Field(
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
            allowed_categories = {"serum", "toner", "sunscreen", "moisturizer", "face-mask", "body-wash", "shampoo", "conditioner", "hair-mask"}
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