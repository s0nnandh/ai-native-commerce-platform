"""
Minimal product lookup for the conversational store.
"""
import json
import os
from typing import List, Dict, Any, Optional
import structlog
from pathlib import Path

from utils.product import Product

logger = structlog.get_logger()


class ProductLookupManager:
    """Simple product data manager for small datasets."""
    
    def __init__(self, products_file: Optional[str] = None):
        """Load products from JSON file."""
        self.products_file = products_file or self._get_products_file_path() 
        self._products: List[Product] = []
        self._load_products()
        
        logger.info("products_loaded", count=len(self._products))
    
    def _get_products_file_path(self) -> str:
        """Get path to products.json file."""
        current_dir = Path(__file__).parent.parent
        return str(current_dir / "data" / "products.json")
    
    def _load_products(self):
        """Load products from JSON file."""
        try:
            # logger.info("load_products", product_file=self.products_file)
            
            with open(self.products_file, 'r') as f:
                products_data = json.load(f)
            
            self._products = [Product(**item) for item in products_data]
            
        except Exception as e:
            logger.error("failed_to_load_products", error=str(e))
            self._products = []
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get product by ID (linear scan)."""
        for product in self._products:
            if product.product_id == product_id:
                return product
        return None
    
    def filter_products_by_constraints(
        self, 
        products: List[Product], 
        keywords: List[str],
        concerns: List[str],
        top_ingredients: List[str],
        avoid_ingredients: List[str],
        name: List[str],
    ) -> List[Product]:
        """Filter products based on user constraints."""
        filtered_products = []
        try:
            for product in products:
                # Check if the product matches all the constraints
                if (any(keyword.lower() in product.tags_list for keyword in keywords) and
                    any(concern.lower() in product.tags_list for concern in concerns) and
                    any(name.lower() in product.name.lower() for name in name) and
                    any(ingredient.lower() in product.ingredients_list for ingredient in top_ingredients) and
                    not any(ingredient.lower() in product.ingredients_list for ingredient in avoid_ingredients)):
                    filtered_products.append(product)
        except Exception as e:
            logger.error("filter_products_error", error=str(e))
            return products

        return filtered_products if len(filtered_products) > 0 else products
    
    def get_all_products(self) -> List[Product]:
        """Get all products."""
        return self._products


# Global instance
product_lookup_manager = ProductLookupManager()