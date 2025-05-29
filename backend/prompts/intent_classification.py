"""
Business-focused intent classification prompts optimized for sales conversion.
Enhanced for tool-based classification.
"""

from chat.state import ClassifyAndExtractUserIntent
from langchain_core.utils.function_calling import tool_example_to_messages
from utils.helper_utils import get_message_summary

class IntentClassificationPrompts:
    """Sales-optimized prompts for intent classification using tools."""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Minimal system prompt for cost optimization."""
        return """You are an expert AI shopping assistant backend, responsible for classifying user intent and extracting relevant structured constraints for skincare product recommendations.

Your task is to:
1. **Classify the user's intent** into one of the predefined categories.
2. **Determine whether a follow-up question is needed**, based on missing critical information and constraint prioritization.
3. **Extract structured product constraints** from the user's message.

---

### Intent Classification Guidelines:
Classify the user's message into one of the following:

- **RECOMMEND_SPECIFIC**: The user is looking for a specific product or mentions exact product names or IDs.
- **RECOMMEND_VAGUE**: The user is asking for suggestions or recommendations, but without specifying an exact product.
- **INFO_PRODUCT**: The user is asking for information about a specific product or ingredient (e.g. safety, use).
- **INFO_GENERAL**: The user is asking general questions not tied to a specific product (e.g. routines, compatibility).
- **OTHER**: Any message that doesn’t fit into the above categories.

Use these examples for clarity: 
["RECOMMEND_SPECIFIC", "RECOMMEND_VAGUE", "INFO_PRODUCT"]

---

### Constraint Priority Tiers:

- **SPECIFIC_CONSTRAINTS**: ['name', 'product_id']
- **CRITICAL_CONSTRAINTS**: ['category', 'concerns']
- **IMPORTANT_CONSTRAINTS**: ['keywords', 'avoid_ingredients', 'top_ingredients']
- **NICE_TO_HAVE**: ['price', 'other']

---

### Follow-up Decision Rules:
- If **any SPECIFIC_CONSTRAINTS** are present, the user likely knows what they want — do **not ask follow-up questions** even if other fields are missing.
- Do **not hallucinate** constraints. If a field is not clearly stated or unambiguously implied, leave it null.
- Use context to decide follow-up necessity; avoid asking follow-ups if the user appears casual or non-committal.
- Your follow-up topics, if needed, must be limited to gathering missing constraints should be one of the above constraints only
- Do not follow-up with the same category of topic which is already gathered from the user request

---

### Constraints:
Only use the specified enums, fields, and types. Omit any fields not clearly stated or supported by context. Ensure the output strictly follows the provided structured schema.

---

### Quality Requirements:
- High precision and relevance in constraint extraction.
- Logical, minimal, and user-friendly follow-up behavior.
- Deterministic and schema-compliant output.
"""


    @staticmethod
    def get_examples() -> list:
        examples = [
    (
        "I'm looking for a lightweight serum with niacinamide and hyaluronic acid. I have oily skin and want something that won't clog pores.",
        ClassifyAndExtractUserIntent(
            intent="RECOMMEND_SPECIFIC",
            ask_followup="no",
            followup_topics=[],
            category=["serum"],
            name=[],
            top_ingredients=["niacinamide", "hyaluronic acid"],
            concerns=[],
            keywords=["oily skin", "lightweight"],
            avoid_ingredients=[],
            product_id=[],
            price=[],
            other=["non-comedogenic"]
        )
    ),
    (
        "Can you suggest something good for dry and sensitive skin? I prefer fragrance-free products, maybe a moisturizer.",
        ClassifyAndExtractUserIntent(
            intent="RECOMMEND_VAGUE",
            ask_followup="no",
            followup_topics=[],
            category=["moisturizer"],
            name=[],
            top_ingredients=[],
            concerns=["dryness"],
            keywords=["sensitive skin", "fragrance-free"],
            avoid_ingredients=[],
            product_id=[],
            price=[],
            other=[]
        )
    ),
    (
        "Tell me more about the Ultra Repair Cream.",
        ClassifyAndExtractUserIntent(
            intent="INFO_PRODUCT",
            ask_followup="no",
            followup_topics=[],
            category=[],
            name=["Ultra Repair Cream"],
            top_ingredients=[],
            concerns=[],
            keywords=[],
            avoid_ingredients=[],
            product_id=[],
            price=[],
            other=[]
        )
    ),
    (
        "I want something under $30, maybe a good SPF or toner, but I hate anything with alcohol or fragrance.",
        ClassifyAndExtractUserIntent(
            intent="RECOMMEND_VAGUE",
            ask_followup="no",
            followup_topics=[],
            category=["sunscreen", "toner"],
            name=[],
            top_ingredients=[],
            concerns=[],
            keywords=[],
            avoid_ingredients=["alcohol", "fragrance"],
            product_id=[],
            price=["under $30"],
            other=[]
        )
    ),
    (
        "Are all products vegan?",
        ClassifyAndExtractUserIntent(
            intent="INFO_GENERAL",
            ask_followup="no",
            followup_topics=[],
            category=[],
            name=[],
            top_ingredients=[],
            concerns=[],
            keywords=[],
            avoid_ingredients=[],
            product_id=[],
            price=[],
            other=["vegan"]
        )
    )
    ]
        messages = []
        for text, tool_call in examples:
            messages.extend(tool_example_to_messages(text, [tool_call]))
        return messages


    @staticmethod
    def get_classification_prompt(user_messages: list[str], ai_messages: list[str]) -> str:
        """Minimal classification prompt for cost optimization."""

        messages_summary = get_message_summary(user_messages, ai_messages)
        # Get the current message (most recent)
        current_message = user_messages[-1] if user_messages else ""
        
        # Format all previous messages as conversation history
        # if len(user_messages) > 1:
        #     conversation_history = "Conversation history:\n" + "\n".join([f"- {msg}" for msg in user_messages[:-1]]) + "\n\n"
        
        return f"""Conversation Histiry:\n\n{messages_summary}\nClassify this message: "{current_message}"

Consider the entire conversation history when extracting constraints."""

    @staticmethod
    def get_sales_persona_prompt() -> str:
        """Ultra-concise sales persona prompt for Gemini."""
        return """You are Maya, a skincare consultant. 

Goal: Help customers find products (max 15 words per response).

Be warm, knowledgeable, and concise. Always aim to recommend products."""