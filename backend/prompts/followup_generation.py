from utils.helper_utils import get_message_summary

"""
Business-focused followup prompts optimized for sales conversion.
"""
class FollowupPrompts:
    """Smart followup question generation for business conversion."""


    @staticmethod
    def get_system_prompt() -> str:
        """Minimal system prompt for cost optimization."""
        return """You are an expert AI shopping assistant for EverGrow Labs, responsible for generating follow-up questions to help recommend skincare products.

Your task is to:
1. **Generate a concise follow-up question** based on the conversation history and missing product constraints.
2. **Base the follow-up on what the user has said so far** and what important details are missing.
3. **Only ask about the most relevant missing information** from the list provided.
4. **Ask naturally** — as if you're in a helpful conversation, not filling a form.

### Follow-up Generation Rules:
- The follow-up should be **brief, contextually relevant**, and limited to gathering missing constraints and 10-12 words max.
- When asking about a missing constraint, naturally include a few relevant examples to guide the user.
- Do **not hallucinate** constraints. If a field is not clearly stated or unambiguously implied, leave it. Do not add it.

### Constraints:
Only use the specified enums, fields, and types. Omit any fields not clearly stated or supported by context. Ensure the output strictly follows the provided structured schema.

### Quality Requirements:
- High precision and relevance in follow up question.
- Logical, minimal, and user-friendly follow-up behavior.
- Deterministic and schema-compliant output.
"""

    @staticmethod
    def get_examples() -> list:
        example_messages = [
    {"role": "user", "content": "I'm looking for a face product that suits me."},
    {"role": "system", "content": "What type of product are you looking for — serum, moisturizer, or sunscreen?"},
    {"role": "user", "content": "What’s a good toner?"},
    {"role": "system", "content": "Any concerns like dryness, acne, or sensitivity?"},
    {"role": "user", "content": "Can you help me find a good product?"},
    {"role": "system", "content": "What’s your main goal — hydration, brightening, or oil control?"},
    {"role": "user", "content": "I'm shopping for skincare."},
    {"role": "system", "content": "Do you prefer any textures like gel or cream?"},
    {"role": "user", "content": "I want something budget-friendly."},
    {"role": "system", "content": "Any specific product category you’re looking for, like sunscreen or serum?"},
]
        return example_messages

    
    @staticmethod
    def get_followup_prompt(
    followup_topics: list[str], 
    user_messages: list[str], 
    assistant_messages: list[str] = None,
) -> str:
        """
        Generate a smart follow-up question that fills in missing information
        from the user in a natural, helpful way.
        """
        key_priorities = {
            "name": "specific product name",
            "product_id": "specific product identifier",
            "category": "type of skincare product (e.g., serum, cleanser)",
            "concerns": "primary concerns (e.g., acne, dryness)",
            "keywords": "any preferences or keywords (e.g., hydrating, gentle)",
            "avoid_ingredients": "ingredients they want to avoid",
            "top_ingredients": "preferred active ingredients",
            "price": "price budget or range",
            "other": "anything else that could help personalize"
        }

        instruction ="""
            Based on the conversation above and the missing information
            Return one natural, clear question that will help gather the most important missing piece of information
        """

        # TODO: Add limit in the messages used
        messages_summary = get_message_summary(user_messages, assistant_messages)

        missing_info_summary = ", ".join(key_priorities.get(k, k) for k in followup_topics)

        prompt = "\n".join([
            f"\n--- Conversation so far ---\n{messages_summary}",
            f"\n--- Missing information to ask about ---\n{missing_info_summary}",
            f"\n{instruction}"
        ])
        return prompt