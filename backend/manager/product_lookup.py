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
            logger.info("load_products", product_file=self.products_file)
            if not os.path.exists(self.products_file):
                self._create_sample_data()
            
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
        constraints: Dict[str, Any]
    ) -> List[Product]:
        """Filter products based on user constraints."""
        if not constraints:
            return products
        
        filtered = products
        
        # Filter by category
        if constraints.get('category'):
            category = constraints['category'].lower()
            filtered = [p for p in filtered if p.category.lower() == category]
        
        # Filter by price cap
        if constraints.get('price_cap'):
            price_cap = float(constraints['price_cap'])
            filtered = [p for p in filtered if p.price_usd <= price_cap]
        
        # Filter by avoid ingredients
        if constraints.get('avoid_ingredients'):
            avoid_ingredients = [ing.lower() for ing in constraints['avoid_ingredients']]
            filtered = [p for p in filtered 
                       if not any(avoid_ing in ing.lower() 
                                for ing in p.ingredients_list 
                                for avoid_ing in avoid_ingredients)]
        
        return filtered
    
    def get_all_products(self) -> List[Product]:
        """Get all products."""
        return self._products
    
    def _create_sample_data(self):
        """Create sample products.json if missing."""
        sample_products = [
            {
                "product_id": "SKU001",
                "name": "Gentle Daily Cleanser",
                "category": "cleanser",
                "description": "A mild, soap-free cleanser suitable for all skin types.",
                "top_ingredients": "Water; Glycerin; Cocamidopropyl Betaine; Sodium Lauroyl Sarcosinate",
                "tags": "gentle|daily|sensitive-skin",
                "price_usd": 24.99,
                "margin_percent": 45.2
            },
            {
                "product_id": "SKU002", 
                "name": "Niacinamide 10% Serum",
                "category": "serum",
                "description": "High-strength niacinamide serum to reduce blemishes and regulate oil production.",
                "top_ingredients": "Water; Niacinamide; Pentylene Glycol; Zinc PCA",
                "tags": "niacinamide|oil-control|acne",
                "price_usd": 18.50,
                "margin_percent": 52.1
            },
            {
                "product_id": "SKU003",
                "name": "Hyaluronic Acid Moisturizer", 
                "category": "moisturizer",
                "description": "Lightweight moisturizer with multiple types of hyaluronic acid for intense hydration.",
                "top_ingredients": "Water; Sodium Hyaluronate; Glycerin; Squalane",
                "tags": "hydrating|lightweight|hyaluronic-acid",
                "price_usd": 32.00,
                "margin_percent": 38.7
            },
            {
                "product_id": "SKU004",
                "name": "Vitamin C Brightening Serum",
                "category": "serum", 
                "description": "Stabilized vitamin C serum with 15% L-Ascorbic Acid.",
                "top_ingredients": "Water; L-Ascorbic Acid; Propylene Glycol; Alpha Tocopherol",
                "tags": "vitamin-c|brightening|antioxidant",
                "price_usd": 42.75,
                "margin_percent": 41.3
            },
            {
                "product_id": "SKU005",
                "name": "Retinol 0.5% Night Treatment",
                "category": "treatment",
                "description": "Gentle retinol formulation for anti-aging and skin renewal.",
                "top_ingredients": "Squalane; Retinol; Caprylic/Capric Triglyceride; Tocopherol",
                "tags": "retinol|anti-aging|night",
                "price_usd": 38.99,
                "margin_percent": 48.6
            }
        ]
        
        os.makedirs(os.path.dirname(self.products_file), exist_ok=True)
        with open(self.products_file, 'w') as f:
            json.dump(sample_products, f, indent=2)


# Global instance
product_lookup_manager = ProductLookupManager()