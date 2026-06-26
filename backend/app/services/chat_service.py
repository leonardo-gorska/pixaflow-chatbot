from sqlalchemy.orm import Session
from app.services.inventory_service import InventoryService
from app.services.gemini_service import GeminiService
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.inventory_service = InventoryService(db)
        self.gemini_service = GeminiService()
    
    def _extract_intent_and_product(self, message: str) -> dict:
        """
        Extract intent and product from user message using Gemini.
        """
        try:
            intent_data = self.gemini_service.extract_intent_and_product(message)
            return intent_data
        except Exception as e:
            logger.error(f"Error extracting intent: {e}")
            return {"intent": "search_product", "product": message.lower()}
    
    def _search_product(self, product_name: str):
        """
        Search for product in the database.
        """
        if product_name:
            return self.inventory_service.search_product(product_name)
        return None
    
    def _format_response(self, product, intent: str, message: str) -> str:
        """
        Format response based on intent and product data.
        """
        product_data = product.to_dict()
        
        # Customize response based on intent
        if intent == "check_price":
            prompt = f"""Você é um atendente de mercado educado.
O usuário perguntou sobre o preço do produto.
Dados do produto: {product_data}
Pergunta: {message}
Responda focando no preço, em português brasileiro."""
            try:
                return self.gemini_service.generate_response(prompt)
            except Exception:
                return f"O {product_data['name']} custa R${product_data['price']:.2f}."
        
        elif intent == "check_quantity":
            prompt = f"""Você é um atendente de mercado educado.
O usuário perguntou sobre a quantidade do produto.
Dados do produto: {product_data}
Pergunta: {message}
Responda focando na quantidade disponível, em português brasileiro."""
            try:
                return self.gemini_service.generate_response(prompt)
            except Exception:
                return f"Temos {product_data['quantity']} unidades de {product_data['name']} em estoque."
        
        else:
            # Default: general product info
            return self.gemini_service.format_response_with_fallback(product_data, message)
    
    def process_message(self, message: str) -> str:
        """
        Process a user message and generate a response.
        Uses Gemini to extract intent and product name before querying the database.
        """
        # Extract intent and product
        intent_data = self._extract_intent_and_product(message)
        intent = intent_data.get("intent", "search_product")
        product_name = intent_data.get("product")
        
        # Search for product
        product = self._search_product(product_name)
        
        if product:
            response = self._format_response(product, intent, message)
        else:
            # Handle no product found with fallback
            try:
                response = self.gemini_service.format_no_product_response(message)
            except Exception as e:
                logger.error(f"Error formatting no product response: {e}")
                response = "Desculpe, não encontrei esse produto no nosso estoque. Que tal perguntar sobre arroz, feijão, leite ou café?"
        
        return response
