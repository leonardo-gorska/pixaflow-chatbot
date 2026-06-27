import json
import logging
import re
from typing import Optional

import google.generativeai as genai

from app.config import get_settings

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self):
        settings = get_settings()
        self.enabled = bool(settings.gemini_api_key)
        self.model: Optional[genai.GenerativeModel] = None

        if self.enabled:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel(settings.gemini_model)

    def generate_response(self, prompt: str) -> str:
        if not self.enabled or self.model is None:
            raise RuntimeError("Gemini API key is not configured.")

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as exc:
            logger.error("Error generating Gemini response: %s", exc)
            raise

    def format_product_response(self, product_data: dict, user_query: str) -> str:
        prompt = f"""Você é um atendente de mercado educado e prestativo.
Responda usando apenas os dados do produto abaixo.
Não invente produtos, preços, quantidades ou promoções.

Dados do produto:
{product_data}

Pergunta do usuário: {user_query}

Responda em português brasileiro, de forma breve e natural."""

        return self.generate_response(prompt)

    def format_no_product_response(self, user_query: str) -> str:
        prompt = f"""Você é um atendente de mercado educado.
O usuário perguntou sobre: "{user_query}"
Esse produto não foi encontrado no estoque.
Responda em português brasileiro, de forma breve, e sugira perguntar por arroz, feijão, leite ou café."""

        return self.generate_response(prompt)

    def _clean_product_name(self, text: str) -> str:
        text = re.sub(r"[^\w\s]", " ", text.lower())
        common_words = {
            "tem",
            "temos",
            "quanto",
            "quanta",
            "quantos",
            "quantas",
            "custa",
            "custam",
            "existe",
            "existem",
            "o",
            "a",
            "os",
            "as",
            "um",
            "uma",
            "uns",
            "umas",
            "de",
            "da",
            "do",
            "em",
            "para",
            "por",
            "é",
            "são",
            "está",
            "estão",
        }
        words = text.split()
        filtered_words = [word for word in words if word not in common_words and len(word) > 2]
        return " ".join(filtered_words)

    def extract_intent_and_product(self, message: str) -> dict:
        prompt = f"""Analise a mensagem do usuário e extraia a intenção e o nome do produto.
Responda apenas em JSON válido com as chaves "intent", "product" e "category".

Intenções possíveis:
- "greeting"
- "farewell"
- "thanks"
- "search_product"
- "check_quantity"
- "check_price"
- "check_total_products"
- "check_category"
- "check_hours"
- "check_location"
- "check_payment"
- "check_promotions"
- "order_product"
- "general"

Mensagem do usuário: "{message}"

Regras:
1. "olá", "ola", "oi", "bom dia", "boa tarde" e "boa noite" são greeting.
2. Perguntas como "quantos cafés tem?" são check_quantity com product "café".
3. Perguntas como "quais cafés tem?" ou "tem café?" são search_product com product "café".
4. Frases como "quero café" ou "separa 2 cafés" são order_product com product "café".
4. Perguntas como "o que vocês vendem?" ou "quais produtos tem?" são check_total_products.
5. Horário de funcionamento é check_hours.
6. Endereço ou localização é check_location.
7. Formas de pagamento é check_payment.
8. Promoções, ofertas ou descontos é check_promotions.

Exemplo:
{{"intent": "check_quantity", "product": "café", "category": null}}"""

        try:
            response_text = self.generate_response(prompt)
            if response_text.startswith("```"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(response_text)
        except Exception as exc:
            logger.info("Gemini intent extraction unavailable, using local fallback: %s", exc)
            return {
                "intent": "search_product",
                "product": self._clean_product_name(message),
                "category": None,
            }

    def format_response_with_fallback(self, product_data: dict, user_query: str) -> str:
        try:
            return self.format_product_response(product_data, user_query)
        except Exception:
            product_name = product_data.get("name", "Produto")
            price = float(product_data.get("price", 0))
            quantity = product_data.get("quantity", 0)
            description = product_data.get("description", "")
            return (
                f"Sim! Temos {product_name}. {description}. "
                f"Preço: R$ {price:.2f}. Quantidade: {quantity} unidades."
            )
