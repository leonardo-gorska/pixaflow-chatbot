from sqlalchemy.orm import Session
from app.services.inventory_service import InventoryService
from app.services.gemini_service import GeminiService
from typing import Optional


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.inventory_service = InventoryService(db)
        self.gemini_service = GeminiService()
    
    def process_message(self, message: str) -> str:
        """
        Process a user message and generate a response.
        Uses Gemini to extract intent and product name before querying the database.
        """
        # Extract intent and product using Gemini
        intent_data = self.gemini_service.extract_intent_and_product(message)
        product_name = intent_data.get("product")
        
        # Search for product in the database
        if product_name:
            product = self.inventory_service.search_product(product_name)
        else:
            product = None
        
        if product:
            product_data = product.to_dict()
            # Use fallback in case Gemini fails
            response = self.gemini_service.format_response_with_fallback(product_data, message)
        else:
            # Handle no product found with fallback
            try:
                response = self.gemini_service.format_no_product_response(message)
            except Exception:
                response = "Desculpe, não encontrei esse produto no nosso estoque. Que tal perguntar sobre arroz, feijão, leite ou café?"
        
        return response
