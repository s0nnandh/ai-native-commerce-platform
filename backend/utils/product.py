from typing import List
from pydantic import BaseModel

class Product(BaseModel):
    """Product model matching the provided schema."""
    product_id: str
    name: str
    category: str
    description: str
    top_ingredients: str  # semicolon-delimited
    tags: str  # pipe-delimited
    price_usd: float
    margin_percent: float
    
    @property
    def ingredients_list(self) -> List[str]:
        """Convert semicolon-delimited ingredients to list."""
        return [ing.strip() for ing in self.top_ingredients.split(';') if ing.strip()]
    
    @property
    def tags_list(self) -> List[str]:
        """Convert pipe-delimited tags to list."""
        return [tag.strip() for tag in self.tags.split('|') if tag.strip()]