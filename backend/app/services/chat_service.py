from sqlalchemy.orm import Session
from app.services.inventory_service import InventoryService
from app.services.gemini_service import GeminiService
from typing import Optional
import logging
import re

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
            # Fallback: if Gemini fails to recognize common patterns, use regex
            if self._is_gemini_failing(intent_data, message):
                return self._extract_intent_fallback(message)
            return intent_data
        except Exception as e:
            logger.error(f"Error extracting intent: {e}")
            return self._extract_intent_fallback(message)
    
    def _is_gemini_failing(self, intent_data: dict, message: str) -> bool:
        """
        Check if Gemini is failing to recognize common patterns.
        """
        intent = intent_data.get("intent", "search_product")
        product = intent_data.get("product")
        message_lower = message.lower()
        
        # If Gemini says it's a product search but the message is clearly a greeting
        if intent == "search_product" and product:
            greeting_patterns = ["ola", "olá", "oi", "bom dia", "boa tarde", "boa noite"]
            if any(greeting in message_lower for greeting in greeting_patterns):
                return True
        
        # If Gemini says it's a product search but the message asks about total products
        if intent == "search_product" and product:
            total_patterns = ["quais produtos", "o que vendem", "o que vocês vendem", "lista de produtos"]
            if any(pattern in message_lower for pattern in total_patterns):
                return True
        
        return False
    
    def _extract_intent_fallback(self, message: str) -> dict:
        """
        Fallback intent extraction using regex patterns.
        """
        message_lower = message.lower()
        
        # Greeting patterns
        if re.match(r'^(ola|olá|oi|bom dia|boa tarde|boa night|eai|eae|hey|hi|hello)', message_lower.strip()):
            return {"intent": "greeting", "product": None, "category": None}
        
        # Farewell patterns
        if re.match(r'^(tchau|adeus|ate logo|bye|falou|xau|adeus)', message_lower.strip()):
            return {"intent": "farewell", "product": None, "category": None}
        
        # Thanks patterns
        if re.match(r'^(obrigado|obrigada|valeu|thanks|agradecido|agradecida)', message_lower.strip()):
            return {"intent": "thanks", "product": None, "category": None}
        
        # Total products patterns
        if re.search(r'(quais produtos|o que vendem|o que vocês vendem|lista de produtos|todos os produtos)', message_lower):
            return {"intent": "check_total_products", "product": None, "category": None}
        
        # Category patterns
        category_match = re.search(r'(quais|quao|que)\s+(\w+)\s+(tem|existem|vende|vocês tem|vocês vendem)', message_lower)
        if category_match:
            category = category_match.group(2)
            return {"intent": "check_category", "product": None, "category": category}
        
        # Hours patterns
        if re.search(r'(horario|horário|abre|fecha|funciona|aberto|fechado)', message_lower):
            return {"intent": "check_hours", "product": None, "category": None}
        
        # Location patterns
        if re.search(r'(onde fica|localizacao|localização|endereco|endereço|fica onde)', message_lower):
            return {"intent": "check_location", "product": None, "category": None}
        
        # Payment patterns
        if re.search(r'(pagamento|pagar|aceita|formas|cartão|cartao|dinheiro|pix|debito|crédito|credito)', message_lower):
            return {"intent": "check_payment", "product": None, "category": None}
        
        # Promotions patterns
        if re.search(r'(promoção|promocao|desconto|oferta|promo|promoções)', message_lower):
            return {"intent": "check_promotions", "product": None, "category": None}
        
        # Quantity patterns
        quantity_match = re.search(r'quantos?\s+(\w+)', message_lower)
        if quantity_match:
            product = quantity_match.group(1)
            return {"intent": "check_quantity", "product": product, "category": None}
        
        # Price patterns
        price_match = re.search(r'(quanto custa|preço do|valor do|preco do)\s+(\w+)', message_lower)
        if price_match:
            product = price_match.group(2)
            return {"intent": "check_price", "product": product, "category": None}
        
        # Default: search for product
        return {"intent": "search_product", "product": message_lower, "category": None}
    
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
        category = intent_data.get("category")
        
        # Handle greeting
        if intent == "greeting":
            return "Olá! Como posso ajudar você hoje? Pergunte sobre nossos produtos, preços, quantidades em estoque, categorias, horário de funcionamento ou formas de pagamento."
        
        # Handle farewell
        if intent == "farewell":
            return "Até logo! Volte sempre que precisar. Foi um prazer ajudar!"
        
        # Handle thanks
        if intent == "thanks":
            return "Por nada! Estou sempre aqui para ajudar. Precisa de mais alguma coisa?"
        
        # Handle special case: check total products
        if intent == "check_total_products":
            try:
                all_products = self.inventory_service.get_all_products()
                total = len(all_products)
                return f"Temos {total} produtos diferentes no nosso estoque."
            except Exception as e:
                logger.error(f"Error getting total products: {e}")
                return "Desculpe, não consegui verificar a quantidade total de produtos no momento."
        
        # Handle category check
        if intent == "check_category" and category:
            try:
                products = self.inventory_service.get_all_products()
                category_products = [p for p in products if p.category and category.lower() in p.category.lower()]
                if category_products:
                    product_list = ", ".join([p.name for p in category_products])
                    return f"Na categoria {category}, temos: {product_list}."
                else:
                    return f"Não encontramos produtos na categoria {category}. Temos produtos em: Grãos, Laticínios, Bebidas, Massas, Açúcar, Óleos e Farinhas."
            except Exception as e:
                logger.error(f"Error getting category products: {e}")
                return "Desculpe, não consegui verificar os produtos dessa categoria."
        
        # Handle hours
        if intent == "check_hours":
            return "Nosso horário de funcionamento é de segunda a sexta, das 8h às 20h, e aos sábados das 8h às 18h. Domingos fechamos."
        
        # Handle location
        if intent == "check_location":
            return "Estamos localizados na Rua do Mercado, 123 - Centro. Fácil acesso com estacionamento gratuito."
        
        # Handle payment
        if intent == "check_payment":
            return "Aceitamos dinheiro, cartões de crédito/débito (Visa, Mastercard, Elo), PIX e vale-alimentação."
        
        # Handle promotions
        if intent == "check_promotions":
            return "Temos promoções semanais! Esta semana: Arroz Camil 5kg com 15% de desconto e Leite Integral Itambé 1kg leve 3 pague 2. Confira no balcão!"
        
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
