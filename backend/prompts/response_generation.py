"""
Minimal response generation prompts optimized for cost.
"""
from typing import Dict, Any, List
from utils.product import Product

class ResponsePrompts:
    """Lightweight response generation prompts."""
    
    def get_recommendation_prompt(
        self,
        user_query: str,
        products: List[Product], 
        constraints: Dict[str, Any],
        turn_count: int = 1
    ) -> str:
        """Minimal recommendation prompt."""
        
        # Format top 3 products simply
        products_text = ""
        for i, p in enumerate(products[:3], 1):
            products_text += f"{i}. {p.name} (${p.price_usd}, {p.category})\n"
        
        # Format constraints simply  
        constraints_text = ", ".join([f"{k}: {v}" for k, v in constraints.items() if v])
        
        return f"""Recommend skincare products (max 80 words):

Query: {user_query}
Products:
{products_text}
Needs: {constraints_text}

Write friendly recommendation mentioning 1-2 specific products with reasons."""

    def get_informational_prompt(
        self,
        user_question: str,
        context_snippets: List[Dict[str, Any]]
    ) -> str:
        """Minimal informational prompt."""
        
        # Format context simply
        context_text = ""
        for snippet in context_snippets[:3]:  # Max 3 snippets
            context_text += f"[{snippet['id']}] {snippet['content'][:150]}...\n"
        
        return f"""Answer skincare question (max 80 words):

Question: {user_question}
Context:
{context_text}

Answer using context. Cite with [1], [2] etc."""