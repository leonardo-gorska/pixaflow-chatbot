import google.generativeai as genai
from app.config import get_settings
from typing import Optional
import json


class GeminiService:
    def __init__(self):
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response using Gemini AI.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            raise  # Re-raise to allow fallback handling
    
    def format_product_response(self, product_data: dict, user_query: str) -> str:
        """
        Format product information into a natural response using Gemini.
        """
        prompt = f"""Você é um atendente de mercado educado e prestativo.
Sua função é responder perguntas sobre produtos usando APENAS os dados fornecidos abaixo.
NUNCA invente informações ou produtos que não estão na lista.
Se o produto não existir nos dados, informe educadamente que não o encontrou.

Dados do produto:
{product_data}

Pergunta do usuário: {user_query}

Responda de forma natural e amigável, em português brasileiro."""
        
        return self.generate_response(prompt)
    
    def format_no_product_response(self, user_query: str) -> str:
        """
        Generate a response when no product is found.
        """
        prompt = f"""Você é um atendente de mercado educado e prestativo.
O usuário perguntou sobre: "{user_query}"
Infelizmente, não encontramos esse produto no nosso estoque.
Responda de forma educada e sugira que o usuário pergunte sobre outros produtos.
Responda em português brasileiro, de forma breve e natural."""
        
        return self.generate_response(prompt)
    
    def extract_intent_and_product(self, message: str) -> dict:
        """
        Extract the user's intent and product name from their message using Gemini.
        Returns a dict with 'intent' and 'product' keys.
        """
        prompt = f"""Analise a mensagem do usuário e extraia a intenção e o nome do produto.
Responda APENAS em formato JSON válido com as chaves "intent" e "product".

Intenções possíveis:
- "search_product": usuário está procurando um produto
- "check_quantity": usuário quer saber a quantidade
- "check_price": usuário quer saber o preço
- "general": pergunta geral sobre o produto

Mensagem do usuário: "{message}"

Exemplo de resposta:
{{"intent": "search_product", "product": "arroz"}}

Se não conseguir identificar um produto específico, retorne null para "product"."""
        
        try:
            response = self.model.generate_content(prompt)
            # Extract JSON from response
            response_text = response.text.strip()
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            result = json.loads(response_text)
            return result
        except Exception as e:
            print(f"Error extracting intent: {e}")
            # Fallback: return the original message as product
            return {"intent": "search_product", "product": message.lower()}
    
    def format_response_with_fallback(self, product_data: dict, user_query: str) -> str:
        """
        Format product response with Gemini, using fallback if it fails.
        """
        try:
            return self.format_product_response(product_data, user_query)
        except Exception:
            # Fallback to simple template
            product_name = product_data.get("name", "Produto")
            price = product_data.get("price", 0)
            quantity = product_data.get("quantity", 0)
            return f"Sim! Temos {product_name}. Preço: R${price:.2f}. Quantidade: {quantity} unidades."
