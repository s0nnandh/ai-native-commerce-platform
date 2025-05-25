"""
ChatState and data models for the conversational store orchestration.
"""
from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from langchain.schema import Document
from utils.product import Product


class Citation(BaseModel):
    """Citation for informational responses."""
    id: str
    snippet: str


class ChatState(BaseModel):
    """
    State object for LangGraph conversation orchestration.
    Tracks conversation context, constraints, and generated outputs.
    """
    session_id: str
    turn_count: int = 0
    
    # Raw I/O
    user_message: Optional[str] = None
    ai_message: Optional[str] = None
    
    # Intent classification and constraints
    intent: Optional[Literal["informational", "specific", "vague", "followup_answered"]] = None
    constraints: Dict[str, Any] = Field(default_factory=dict)
    missing_keys: List[str] = Field(default_factory=list)
    followup_key: Optional[str] = None
    
    # Flow control flags
    ask_followup: bool = False
    
    # Retrieval and outputs
    retrieved_docs: List[Document] = Field(default_factory=list)
    products: List[Product] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    
    @field_validator('intent')
    @classmethod
    def validate_intent(cls, v):
        """Validate intent enum values."""
        if v is not None:
            allowed_intents = {"informational", "specific", "vague", "followup_answered"}
            if v not in allowed_intents:
                raise ValueError(f"Intent must be one of {allowed_intents}, got {v}")
        return v
    
    def merge_constraints(self, new_constraints: Dict[str, Any]) -> None:
        """
        Merge new constraints into existing ones, handling list merging appropriately.
        """
        for key, value in new_constraints.items():
            if key in ['avoid_ingredients', 'desired_ingredients']:
                # Merge lists, avoiding duplicates
                existing = self.constraints.get(key, [])
                if isinstance(existing, list) and isinstance(value, list):
                    merged = list(set(existing + value))
                    self.constraints[key] = merged
                else:
                    self.constraints[key] = value if isinstance(value, list) else [value]
            else:
                # Direct assignment for non-list constraints
                self.constraints[key] = value
    
    def get_constraint_priority_order(self) -> List[str]:
        """
        Return constraint keys in priority order for followup questions.
        Safety-first approach with critical constraints prioritized.
        """
        return [
            'category',           # Critical: narrow search space
            'skin_concern',       # Critical: core need identification
            'avoid_ingredients',  # Important: safety concerns
            'target_sku',         # Important: direct product request
            'desired_ingredients', # Nice-to-have: preference
            'price_cap',          # Nice-to-have: budget
            'finish'             # Nice-to-have: texture preference
        ]
    
    def get_constraint_groups(self) -> Dict[str, List[str]]:
        """
        Group constraints by criticality for smarter followup logic.
        """
        return {
            'CRITICAL_CONSTRAINTS': ['category', 'skin_concern'],
            'IMPORTANT_CONSTRAINTS': ['avoid_ingredients', 'target_sku'],
            'NICE_TO_HAVE': ['desired_ingredients', 'price_cap', 'finish']
        }
    
    def should_ask_followup(self) -> tuple[bool, str]:
        """
        Determine if we should ask a followup question based on:
        1. Turn count (max 3 turns total)
        2. Constraint criticality
        3. Information completeness
        """
        # Never ask after 3 turns
        if self.turn_count >= 3:
            return False, None
            
        constraint_groups = self.get_constraint_groups()
        
        # Always ask about critical constraints if missing (turns 0-2)
        for key in constraint_groups['CRITICAL_CONSTRAINTS']:
            if key in self.missing_keys:
                return True, key
        
        # Ask about important constraints on first 2 turns
        if self.turn_count < 2:
            for key in constraint_groups['IMPORTANT_CONSTRAINTS']:
                if key in self.missing_keys:
                    return True, key
        
        # Only ask about nice-to-have on first turn and if we have very little info
        if self.turn_count == 0 and len(self.constraints) < 2:
            for key in constraint_groups['NICE_TO_HAVE']:
                if key in self.missing_keys:
                    return True, key
                    
        return False, None
    
    def reset_for_new_turn(self) -> None:
        """Reset state for a new conversation turn while preserving session context."""
        self.user_message = None
        self.ai_message = None
        self.ask_followup = False
        self.followup_key = None
        self.retrieved_docs = []
        self.products = []
        self.citations = []


class IntentClassificationResult(BaseModel):
    """Result from intent classification LLM call."""
    intent: Literal["informational", "specific", "vague", "followup_answered"]
    ask_followup: bool
    followup_question: Optional[str] = None
    detected_constraints: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('intent')
    @classmethod
    def validate_intent_enum(cls, v):
        """Validate intent enum values."""
        allowed_intents = {"informational", "specific", "vague", "followup_answered"}
        if v not in allowed_intents:
            raise ValueError(f"Intent must be one of {allowed_intents}, got {v}")
        return v


class AssistResponse(BaseModel):
    """Response format for the /api/assist endpoint."""
    text: str
    ask_followup: bool
    followup_key: Optional[str] = None
    products: List[Dict[str, Any]] = Field(default_factory=list)
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    latency_ms: int