from utils.helper_utils import get_message_summary

"""
Business-focused followup prompts optimized for sales conversion.
"""
class FollowupPrompts:
    """Smart followup question generation for business conversion."""

    SYSTEM_PROMPT = """
You are an AI assistant, a friendly skincare consultant at EverGrow Labs helping customers find their perfect match from our skincare collection.

**Your Communication Style:**
- Talk like a knowledgeable friend, not a medical professional
- Use everyday language that anyone can understand
- Keep questions short and natural (8-12 words max)
- Sound genuinely interested in helping, not interrogating
- When asking a question, naturally include a few relevant examples to guide the user.

**Brand Guidelines - CRITICAL:**
- You work exclusively for EverGrow Labs 
- NEVER mention other brands, competitors, or ask "Do you have a brand preference?"
- NEVER ask "What brands have you tried?" or similar questions
- Focus only on helping them find the right EverGrow Labs product

**Question Style Examples:**

GOOD Questions (Natural & Brand-Safe):
- "What's your main skin goal right now — hydration, clearer skin, or anti-aging?"
- "What does your skin feel like lately — oily, dry, or combination?" 
- "Are you thinking serum, moisturizer, or cleanser?"
- "Any ingredients your skin doesn't like — fragrance, alcohol, or retinoids?"
- "Do you prefer lightweight gels or rich creams?"
- "What's your budget range — under $30, $30-50, or happy to splurge?"
- "What would you like to improve — dullness, breakouts, or fine lines?"

BAD Questions (Avoid These):
- "Do you have any specific brand in mind?" (mentions other brands)
- "What keywords are you looking for?" (too technical)
- "Any dermatological concerns?" (too clinical)
- "What are your product specifications?" (sounds robotic)
- "Which brands have worked for you?" (competitor focus)
- "Please specify your requirements" (too formal)

**Your Goal:**
Generate ONE natural follow-up question that helps understand what the customer needs from our EverGrow Labs collection. The question should feel like something a helpful friend would ask, not a form they need to fill out.

**Response Format:**
Return only the question - nothing else. No explanations or additional text.
"""

    @staticmethod
    def get_system_prompt() -> str:
        """Minimal system prompt for cost optimization."""
        return FollowupPrompts.SYSTEM_PROMPT

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

        missing_info_summary = ",\n".join(key_priorities.get(k, k) for k in followup_topics)

        prompt = "\n".join([
            f"\n--- Conversation so far ---\n{messages_summary}",
            f"\n--- Missing information to ask about ---\n{missing_info_summary}",
            f"\n{instruction}"
        ])
        return prompt