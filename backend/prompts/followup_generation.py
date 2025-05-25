"""
Contextual followup prompts optimized for cost.
"""
from typing import Dict, Any

class FollowupPrompts:
    """Contextual follow-up question generation."""
    
    def get_followup_prompt(
        self,
        followup_key: str, 
        user_message: str,
        existing_constraints: Dict[str, Any],
        turn_count: int
    ) -> str:
        """Generate contextual follow-up question (cost-optimized)."""
        
        # Map constraint keys to natural language
        constraint_focus = {
            "category": "product type",
            "skin_concern": "skin concern", 
            "avoid_ingredients": "ingredients to avoid",
            "desired_ingredients": "preferred ingredients",
            "price_cap": "budget",
            "target_sku": "specific product",
            "finish": "texture preference"
        }
        
        focus = constraint_focus.get(followup_key, followup_key)
        
        # Format existing constraints briefly
        existing_info = ", ".join([f"{k}: {v}" for k, v in existing_constraints.items() if v]) or "none"
        
        return f"""Ask ONE contextual question about {focus} based on their message: "{user_message}"

Existing info: {existing_info}
Keep under 25 words. Be natural and specific to their situation."""