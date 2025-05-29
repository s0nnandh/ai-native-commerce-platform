"""
Minimal response generation prompts optimized for cost.
"""
from typing import Dict, Any, List
from utils.product import Product
from langchain_core.utils.function_calling import tool_example_to_messages
from utils.helper_utils import get_message_summary


class ResponsePrompts:
    """Lightweight response generation prompts."""

    def get_recommendation_system_prompt(self) -> str:
        return """You are a concise assistant that recommends skincare products based on user input and product descriptions.

Rules:
- Respond with a short, specific sentence (max 12–15 words).
- This sentence will appear above a list of products as a section heading.
- DO NOT include product names or prices.
- DO NOT hallucinate product details — use only the input provided.
- Start directly with a tailored summary like: 'Here are some moisturizers for dry and flaky skin'."""


    def get_recommendation_examples(self) -> list:
        example_messages = [
        {"role": "user", "content": "Can you help me find a good moisturizer for dry skin?"},
        {"role": "assistant", "content": "Moisturizers that deeply hydrate and soothe dry, flaky skin."},
        {"role": "user", "content": "My skin is very oily and I get acne often."},
        {"role": "assistant", "content": "Great for oily, acne-prone skin to reduce breakouts and shine."}
    # [
    #     {"role": "user", "content": "What do you recommend for pigmentation and dull skin tone?"},
    #     {"role": "system", "content": "Brightening serums targeting pigmentation and uneven skin tone."}
    # ],
    # [
    #     {"role": "user", "content": "I'm looking for fragrance-free options for sensitive skin."},
    #     {"role": "system", "content": "Fragrance-free formulas designed to calm and protect sensitive skin."}
    # ],
    # [
    #     {"role": "user", "content": "Something lightweight for oily summer skin?"},
    #     {"role": "system", "content": "Lightweight, gel-textured options perfect for oily skin in humid weather."}
    # ],
    # [
    #     {"role": "user", "content": "Do you have sunscreens that won't clog pores?"},
    #     {"role": "system", "content": "Non-comedogenic sunscreens that protect without clogging pores."}
    # ],
    # [
    #     {"role": "user", "content": "I prefer vegan products and have redness issues."},
    #     {"role": "system", "content": "Vegan-friendly products formulated to reduce redness and irritation."}
    # ],
    # [
    #     {"role": "user", "content": "Looking for a toner with salicylic acid for blackheads."},
    #     {"role": "system", "content": "Salicylic acid toners that gently exfoliate and unclog pores."}
    # ],
    # [
    #     {"role": "user", "content": "Any suggestions for anti-aging skincare with retinol?"},
    #     {"role": "system", "content": "Retinol-based products to target fine lines and signs of aging."}
    # ],
    # [
    #     {"role": "user", "content": "I want something alcohol-free and lightweight."},
    #     {"role": "system", "content": "Alcohol-free and lightweight picks for a clean, breathable feel."}
    # ],
]
        # messages = []
        # for text, tool_call in example_messages:
        #     messages.extend(tool_example_to_messages(text, [tool_call]))
        return example_messages


    
    def get_user_recommendation_prompt(
        self,
        user_messages: list,
        ai_messages: list,
        products: List[Product],
    ) -> str:
        """Ultra-concise recommendation prompt with optional conversation history."""
        
        # Format top 2 products simply
        products_text = ""
        for i, p in enumerate(products[:2], 1):
            products_text += f"{i}. {p.name} - ${p.description}\n"
        
        # Add conversation history if available
        messages_summary = "\n".join(
            [f"User: {m}" for m in user_messages] + 
            [f"Assistant: {m}" for m in (ai_messages or [])]
        )
        
        # Add history to prompt if available
        history_section = f"\nPrevious conversation:\n{messages_summary}" if messages_summary else ""
        
        return f"""Please recommend products based on the above. 

Products:
{products_text}
{history_section}

Follow all instructions from the system prompt.

"""
    
    def get_informational_system_prompt(self) -> str:
        return """You are a helpful and concise assistant that answers skincare-related questions using context and conversation history.

Rules:
- Limit your response to 12–15 words.
- No greetings, no filler, no chit-chat.
- Use only the provided context. Do not make up product names or facts.
- Mention a relevant product if supported by the context.
- Start the answer directly, keep it crisp and factual."""


    def get_informational_examples(self) -> str:
        example_messages = [
        {"role": "user", "content": "Can you help me find a good moisturizer for dry skin?"},
        {"role": "system", "content": "Moisturizers that deeply hydrate and soothe dry, flaky skin."},
        {"role": "user", "content": "My skin is very oily and I get acne often."},
        {"role": "system", "content": "Great for oily, acne-prone skin to reduce breakouts and shine."},
    # [
    #     {"role": "user", "content": "What do you recommend for pigmentation and dull skin tone?"},
    #     {"role": "system", "content": "Brightening serums targeting pigmentation and uneven skin tone."}
    # ],
    # [
    #     {"role": "user", "content": "I’m looking for fragrance-free options for sensitive skin."},
    #     {"role": "system", "content": "Fragrance-free formulas designed to calm and protect sensitive skin."}
    # ],
    # [
    #     {"role": "user", "content": "Something lightweight for oily summer skin?"},
    #     {"role": "system", "content": "Lightweight, gel-textured options perfect for oily skin in humid weather."}
    # ],
    # [
    #     {"role": "user", "content": "Do you have sunscreens that won’t clog pores?"},
    #     {"role": "system", "content": "Non-comedogenic sunscreens that protect without clogging pores."}
    # ],
    # [
    #     {"role": "user", "content": "I prefer vegan products and have redness issues."},
    #     {"role": "system", "content": "Vegan-friendly products formulated to reduce redness and irritation."}
    # ],
    # [
    #     {"role": "user", "content": "Looking for a toner with salicylic acid for blackheads."},
    #     {"role": "system", "content": "Salicylic acid toners that gently exfoliate and unclog pores."}
    # ],
    # [
    #     {"role": "user", "content": "Any suggestions for anti-aging skincare with retinol?"},
    #     {"role": "system", "content": "Retinol-based products to target fine lines and signs of aging."}
    # ],
    # [
    #     {"role": "user", "content": "I want something alcohol-free and lightweight."},
    #     {"role": "system", "content": "Alcohol-free and lightweight picks for a clean, breathable feel."}
    # ],
]
        return example_messages




    def get_informational_prompt(
            self, 
    context_snippets: List[Dict[str, Any]],
    user_messages: list[str],
    ai_messages: list[str]
) -> str:
        """Ultra-concise informational prompt with optional conversation history."""
        
        context_text = "\n".join([f"{snippet.get('id')} - {snippet.get('content')}" for snippet in context_snippets])
        
        # Summarize previous messages
        messages_summary = get_message_summary(user_messages, ai_messages)
        
        history_section = f"\nPrevious conversation:\n{messages_summary}" if messages_summary else ""
        
        return f"""Answer in 12–15 words max.

    User Question: {user_messages[0]}    

    {history_section}

    Context: {context_text}

    Answer concisely using the context. Mention a product only if relevant."""
