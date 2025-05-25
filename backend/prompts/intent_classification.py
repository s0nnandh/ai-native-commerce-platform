"""
Minimal intent classification prompts optimized for cost.
"""

class IntentClassificationPrompts:
    """Lightweight prompts for intent classification."""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Minimal system prompt - tool schema handles constraint definitions."""
        return """Classify user intent and extract skincare constraints:

- "informational": asking about products/ingredients/advice  
- "specific": clear requirements and constraints
- "vague": unclear, needs more information
- "followup_answered": responding to previous question

Use the classify_intent_and_extract_constraints tool."""