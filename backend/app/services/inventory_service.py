from sqlalchemy.orm import Session
from app.database.models import Product
from typing import Optional, List


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
        
        return product
    
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
