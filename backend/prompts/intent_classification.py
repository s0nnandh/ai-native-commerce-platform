"""
Business-focused intent classification prompts optimized for sales conversion.
Enhanced for tool-based classification.
"""

from chat.state import ClassifyAndExtractUserIntent
from langchain_core.utils.function_calling import tool_example_to_messages
from utils.helper_utils import get_message_summary

class IntentClassificationPrompts:
    """Sales-optimized prompts for intent classification using tools."""

    SYSTEM_PROMPT = """
You are an expert AI shopping assistant backend for EverGrow Labs, responsible for classifying user intent and making intelligent decisions about follow-up questions.

Your task is to:
1. **Classify the user's intent** into one of the predefined categories.
2. **Make smart follow-up decisions** - only ask when truly necessary for good recommendations.
3. **Extract structured product constraints** from the user's message without hallucinating.

---

### Intent Classification Guidelines:

Classify the user's message into one of the following:

- **RECOMMEND_SPECIFIC**: The user is looking for a specific product or mentions exact product names or IDs.
- **RECOMMEND_VAGUE**: The user is asking for suggestions or recommendations, but without specifying an exact product.
- **INFO_PRODUCT**: The user is asking for information about a specific product or ingredient (e.g. safety, use).
- **INFO_GENERAL**: The user is asking general questions not tied to a specific product (e.g. routines, compatibility).
- **OTHER**: Any message that doesn't fit into the above categories.

Use these examples for clarity: 
["RECOMMEND_SPECIFIC", "RECOMMEND_VAGUE", "INFO_PRODUCT"]

---

### CRITICAL: Smart Follow-up Decision Logic

**SUFFICIENT INFO - Do NOT ask follow-up (ask_followup = False):**
- User provided **category + concern** (minimum viable for good recommendations)
  Example: "hydrating moisturizer for acne" → Has category + concern = SUFFICIENT
- User mentions **specific product names** or shows they know what they want
- User provided **3+ constraints** from any tier
- **Constraint already mentioned** in conversation history (check previous turns)
- User shows **casual browsing** intent ("just looking", "browsing around")

**NEED MORE INFO - Ask follow-up (ask_followup = True):**
- Intent is **RECOMMEND_VAGUE** AND missing BOTH category AND concerns
- User seems committed but gave minimal info ("I need help")
- Early conversation (≤2 turns) AND user shows purchase intent

**NEVER ask about:**
- Constraints already mentioned by user in previous conversation turns
- Category if user already specified it (even indirectly)
- Information that would only marginally improve recommendations

---

### Constraint Priority Tiers:

**MINIMUM VIABLE INFO**: category + concerns (sufficient for recommendations)
- **SPECIFIC_CONSTRAINTS**: ['name', 'product_id']
- **CRITICAL_CONSTRAINTS**: ['category', 'concerns']
- **IMPORTANT_CONSTRAINTS**: ['keywords', 'avoid_ingredients', 'top_ingredients']
- **NICE_TO_HAVE**: ['price', 'other']

---

### Follow-up Decision Examples:

**GOOD - No Follow-up Needed:**
- "hydrating moisturizer for acne" → Has category + concern = PROCEED
- "vitamin C serum under $30" → Has category + ingredient + price = PROCEED  
- "gentle cleanser for sensitive skin" → Has category + concern = PROCEED
- "the niacinamide serum" → Specific product = PROCEED

**BAD - Avoid These Mistakes:**
- User: "moisturizer for dry skin" → Don't ask: "What type of product?" (they said moisturizer!)
- User: "acne products" → Don't ask: "What's your skin concern?" (they said acne!)
- User: Turn 2 after mentioning "serum" → Don't ask: "Are you looking for serum or moisturizer?"

---

### Quality Requirements:
- **Minimal questioning**: Only ask when recommendations would be significantly poor without the info
- **Memory awareness**: Consider the entire conversation history to avoid redundancy
- **Sufficient info recognition**: Recognize when you have enough to provide good recommendations  
- **User experience focus**: Prioritize quick, helpful recommendations over perfect information gathering

---

### Decision Framework Priority:
1. **Check sufficiency**: Does user have category + concerns? → Sufficient for recommendations
2. **Check history**: Already discussed this constraint? → Don't ask again
3. **Assess commitment**: Casual browser or serious shopper? → Adjust questioning accordingly
4. **Consider turn count**: After 2-3 turns? → Prioritize recommendations over more questions

**GOAL**: Better to give good recommendations with limited info than to over-question users. Most users prefer quick help over detailed interrogation.

---

### Constraints:
Only use the specified enums, fields, and types. Omit any fields not clearly stated or supported by context. Ensure the output strictly follows the provided structured schema.

### Quality Requirements:
- High precision and relevance in constraint extraction.
- Logical, minimal, and user-friendly follow-up behavior.
- Deterministic and schema-compliant output.
"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Minimal system prompt for cost optimization."""
        return IntentClassificationPrompts.SYSTEM_PROMPT


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
        
        return f"""Conversation History:\n\n{messages_summary}\n
        Classify the user intent from the above conversation history"

Consider the entire conversation history when extracting constraints."""

    @staticmethod
    def get_sales_persona_prompt() -> str:
        """Ultra-concise sales persona prompt for Gemini."""
        return """You are Maya, a skincare consultant. 

Goal: Help customers find products (max 15 words per response).

Be warm, knowledgeable, and concise. Always aim to recommend products."""