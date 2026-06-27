from sqlalchemy.orm import Session
from app.database.models import Product
from typing import Optional, List
from difflib import SequenceMatcher


class InventoryService:
    def __init__(self, db: Session):
        self.db = db
    
    def search_product(self, query: str) -> Optional[Product]:
        """
        Search for a product by name (case-insensitive partial match).
        Returns the first matching product or None.
        """
        query_lower = query.lower()
        
        # Try exact match first
        product = self.db.query(Product).filter(
            Product.name.ilike(f"%{query_lower}%")
        ).first()
        
        if product:
            return product
        
        # Try fuzzy matching if no exact match
        all_products = self.db.query(Product).all()
        best_match = None
        best_ratio = 0.6  # Minimum similarity threshold
        
        for prod in all_products:
            # Compare query with product name
            ratio = SequenceMatcher(None, query_lower, prod.name.lower()).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = prod
        
        return best_match
    
    def get_all_products(self) -> List[Product]:
        """
        Get all products in the inventory.
        """
        return self.db.query(Product).all()
    
    def get_product_by_name(self, name: str) -> Optional[Product]:
        """
        Get a product by exact name match.
        """
        return self.db.query(Product).filter(
            Product.name.ilike(name)
        ).first()
