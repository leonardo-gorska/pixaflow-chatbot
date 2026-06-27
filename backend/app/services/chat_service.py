import logging
import re
from typing import Optional

from sqlalchemy.orm import Session

from app.services.gemini_service import GeminiService
from app.services.inventory_service import InventoryService

logger = logging.getLogger(__name__)


class ChatService:
    STOPWORDS = {
        "tem",
        "temos",
        "voces",
        "vocês",
        "vende",
        "vendem",
        "produto",
        "produtos",
        "qual",
        "quais",
        "quanto",
        "quantos",
        "quantas",
        "custa",
        "custam",
        "preco",
        "preço",
        "valor",
        "valores",
        "existe",
        "existem",
        "no",
        "na",
        "nos",
        "nas",
        "do",
        "da",
        "dos",
        "das",
        "de",
        "o",
        "a",
        "os",
        "as",
        "um",
        "uma",
        "ai",
        "aí",
        "estoque",
    }

    def __init__(self, db: Session):
        self.db = db
        self.inventory_service = InventoryService(db)
        self.gemini_service = GeminiService()

    def _normalized_message(self, message: str) -> str:
        return self.inventory_service.normalize_text(message)

    def _clean_product_query(self, message: str) -> Optional[str]:
        normalized = self._normalized_message(message)
        tokens = []

        for token in normalized.split():
            singular = self.inventory_service.singularize_token(token)
            if singular not in self.STOPWORDS and len(singular) > 1:
                tokens.append(singular)

        product_query = " ".join(tokens).strip()
        return product_query or None

    def _extract_intent_fallback(self, message: str) -> dict:
        normalized = self._normalized_message(message)

        if not normalized:
            return {"intent": "greeting", "product": None, "category": None}

        if re.fullmatch(r"(ola|oi|opa|bom dia|boa tarde|boa noite|eai|eae|hey|hello|hi)", normalized):
            return {"intent": "greeting", "product": None, "category": None}

        if re.search(r"\b(tchau|adeus|ate logo|ate mais|bye|falou|xau)\b", normalized):
            return {"intent": "farewell", "product": None, "category": None}

        if re.search(r"\b(obrigado|obrigada|valeu|thanks|agradecido|agradecida)\b", normalized):
            return {"intent": "thanks", "product": None, "category": None}

        if re.search(r"\b(como peco|como pedir|como compro|como comprar|como funciona|fazer pedido|faco pedido|fazer compra|comprar alguma coisa|pedir alguma coisa|ajuda|me ajuda)\b", normalized):
            return {"intent": "help_order", "product": None, "category": None}

        if re.search(r"\b(horario|abre|fecha|funciona|funcionamento|aberto|fechado)\b", normalized):
            return {"intent": "check_hours", "product": None, "category": None}

        if re.search(r"\b(onde fica|localizacao|endereco|fica onde|rua|bairro)\b", normalized):
            return {"intent": "check_location", "product": None, "category": None}

        if re.search(r"\b(telefone|whatsapp|zap|contato|contatar|ligar|numero)\b", normalized):
            return {"intent": "check_contact", "product": None, "category": None}

        if re.search(r"\b(pagamento|pagar|aceita|formas|cartao|dinheiro|pix|debito|credito)\b", normalized):
            return {"intent": "check_payment", "product": None, "category": None}

        if re.search(r"\b(entrega|entregam|entregar|delivery|frete|retirada|retirar)\b", normalized):
            return {"intent": "check_delivery", "product": None, "category": None}

        if re.search(r"\b(troca|trocar|devolucao|devolver|devolvem|reembolso)\b", normalized):
            return {"intent": "check_returns", "product": None, "category": None}

        if re.search(r"\b(promocao|promocoes|desconto|oferta|ofertas|promo)\b", normalized):
            return {"intent": "check_promotions", "product": None, "category": None}

        if re.search(r"\b(categoria|categorias|setor|setores|secao|secoes)\b", normalized):
            return {"intent": "list_categories", "product": None, "category": None}

        if re.search(r"\b(mais barato|menor preco|menor valor|mais em conta|barato)\b", normalized):
            return {"intent": "check_cheapest", "product": None, "category": None}

        if re.search(r"\b(mais caro|maior preco|maior valor|caro)\b", normalized):
            return {"intent": "check_most_expensive", "product": None, "category": None}

        if re.search(r"\b(baixo estoque|pouco estoque|acabando|menos unidades|menor estoque)\b", normalized):
            return {"intent": "check_low_stock", "product": None, "category": None}

        if re.search(r"\b(total de unidades|unidades no total|itens no estoque|total em estoque)\b", normalized):
            return {"intent": "check_total_stock", "product": None, "category": None}

        if re.search(r"\b(quantos produtos|quantidade de produtos|total de produtos)\b", normalized):
            return {"intent": "check_total_products", "product": None, "category": None}

        if normalized in {"quais", "quais produtos", "produtos"} or re.search(
            r"\b(o que|quais produtos|lista|listar|todos os produtos|vendem|voces vendem)\b",
            normalized,
        ):
            return {"intent": "list_products", "product": None, "category": None}

        product = self._clean_product_query(message)

        if re.search(r"\b(preco|valor|custa|custam)\b", normalized):
            return {"intent": "check_price", "product": product, "category": None}

        if re.search(r"\b(quanto|quantos|quantas|quantidade|estoque)\b", normalized):
            return {"intent": "check_quantity", "product": product, "category": None}

        if re.search(r"\b(quais|qual|que)\b", normalized) and product:
            return {"intent": "list_matching_products", "product": product, "category": None}

        return {"intent": "search_product", "product": product, "category": None}

    def _extract_intent_and_product(self, message: str) -> dict:
        local_intent = self._extract_intent_fallback(message)
        if local_intent["intent"] != "search_product" or local_intent.get("product"):
            return local_intent

        try:
            intent_data = self.gemini_service.extract_intent_and_product(message)
            if not intent_data.get("product"):
                intent_data["product"] = local_intent.get("product")
            return intent_data
        except Exception as exc:
            logger.error("Error extracting intent: %s", exc)
            return local_intent

    @staticmethod
    def _format_money(value: float) -> str:
        return f"R$ {float(value):.2f}".replace(".", ",")

    def _format_product_summary(self, product) -> str:
        data = product.to_dict()
        return (
            f"{data['name']} ({data['description']}) - "
            f"{self._format_money(data['price'])}, {data['quantity']} unidades"
        )

    def _format_product_bullet(self, product) -> str:
        data = product.to_dict()
        return (
            f"- {data['name']}\n"
            f"  {data['description']}\n"
            f"  Preço: {self._format_money(data['price'])} | Estoque: {data['quantity']} unidades"
        )

    def _format_product_response(self, product, intent: str, message: str) -> str:
        data = product.to_dict()

        if intent == "check_price":
            return f"O {data['name']} custa {self._format_money(data['price'])}."

        if intent == "check_quantity":
            return f"Temos {data['quantity']} unidades de {data['name']} em estoque."

        try:
            return self.gemini_service.format_response_with_fallback(data, message)
        except Exception:
            return (
                f"Sim! Temos {data['name']}. {data['description']}. "
                f"Preço: {self._format_money(data['price'])}. "
                f"Quantidade: {data['quantity']} unidades."
            )

    def _list_all_products(self) -> str:
        products = self.inventory_service.get_all_products()
        product_list = "\n\n".join(self._format_product_bullet(product) for product in products)
        return f"Temos {len(products)} produtos no estoque:\n\n{product_list}"

    def _list_matching_products(self, query: str) -> str:
        products = self.inventory_service.search_products(query)
        if not products:
            return self._no_product_response(query)

        product_list = "\n\n".join(self._format_product_bullet(product) for product in products)
        return f"Encontrei {len(products)} opção(ões):\n\n{product_list}"

    def _available_product_names(self) -> list[str]:
        return [product.name for product in self.inventory_service.get_all_products()]

    def _no_product_response(self, user_query: str) -> str:
        available_products = self._available_product_names()
        available_text = ", ".join(available_products)

        prompt = f"""Você é um atendente de mercado educado e objetivo.
O usuário perguntou: "{user_query}"
Esse produto ou pedido não foi encontrado no estoque atual.

Produtos disponíveis:
{available_text}

Responda em português brasileiro, de forma curta e natural.
Não invente produtos.
Sugira 2 ou 3 produtos disponíveis e ofereça listar o estoque completo."""

        try:
            return self.gemini_service.generate_response(prompt)
        except Exception:
            suggestions = ", ".join(available_products[:4])
            return (
                "Não encontrei esse item no estoque agora. "
                f"Posso te ajudar com algumas opções que temos, como {suggestions}. "
                "Se quiser, pergunte \"Quais produtos vocês vendem?\" para ver a lista completa."
            )

    def _list_categories(self) -> str:
        products = self.inventory_service.get_all_products()
        categories = sorted({product.category for product in products if product.category})
        return "Trabalhamos com estas categorias: " + ", ".join(categories) + "."

    def _inventory_extreme(self, reverse: bool) -> str:
        products = self.inventory_service.get_all_products()
        product = sorted(products, key=lambda item: float(item.price), reverse=reverse)[0]
        qualifier = "mais caro" if reverse else "mais barato"
        return f"O produto {qualifier} do estoque é {self._format_product_summary(product)}."

    def _low_stock_summary(self) -> str:
        products = sorted(self.inventory_service.get_all_products(), key=lambda item: item.quantity)
        low_stock = products[:3]
        product_list = "\n\n".join(self._format_product_bullet(product) for product in low_stock)
        return f"Os produtos com menor estoque agora são:\n\n{product_list}"

    def _total_stock_summary(self) -> str:
        products = self.inventory_service.get_all_products()
        total_units = sum(product.quantity for product in products)
        return f"Temos {total_units} unidades no estoque, somando todos os produtos cadastrados."

    def process_message(self, message: str) -> str:
        intent_data = self._extract_intent_and_product(message)
        intent = intent_data.get("intent", "search_product")
        product_name = intent_data.get("product")
        category = intent_data.get("category")

        if intent == "greeting":
            return (
                "Olá! Como posso ajudar você hoje? "
                "Pode perguntar sobre produtos, preços, quantidades, horário, endereço ou formas de pagamento."
            )

        if intent == "farewell":
            return "Até logo! Volte sempre que precisar."

        if intent == "thanks":
            return "Por nada! Precisa de mais alguma coisa?"

        if intent == "help_order":
            return (
                "Você pode pedir de um jeito bem simples:\n\n"
                "- Pergunte se temos um produto. Ex.: \"Tem arroz?\"\n"
                "- Consulte preço ou estoque. Ex.: \"Quanto custa o café?\" ou \"Quantos cafés tem?\"\n"
                "- Peça a lista de produtos. Ex.: \"O que vocês vendem?\"\n\n"
                "Depois é só me dizer o produto que você procura."
            )

        if intent in {"check_total_products", "list_products"}:
            return self._list_all_products()

        if intent == "check_category" and category:
            return self._list_matching_products(category)

        if intent == "check_hours":
            return "Nosso horário de funcionamento é de segunda a sexta, das 8h às 20h, e aos sábados das 8h às 18h. Aos domingos fechamos."

        if intent == "check_location":
            return "Estamos na Rua do Mercado, 123 - Centro. Temos estacionamento gratuito."

        if intent == "check_contact":
            return "Você pode falar com o mercado pelo WhatsApp (11) 99999-0000 ou pelo telefone (11) 3333-0000."

        if intent == "check_payment":
            return "Aceitamos dinheiro, cartões de crédito e débito, PIX e vale-alimentação."

        if intent == "check_delivery":
            return "Sim, fazemos entregas na região do Centro. Também é possível retirar o pedido no mercado."

        if intent == "check_returns":
            return "Fazemos troca de produtos com problema mediante apresentação do comprovante. Para perecíveis, pedimos contato no mesmo dia da compra."

        if intent == "check_promotions":
            return "Temos promoções semanais. Hoje, você pode conferir as ofertas no balcão do mercado."

        if intent == "list_categories":
            return self._list_categories()

        if intent == "check_cheapest":
            return self._inventory_extreme(reverse=False)

        if intent == "check_most_expensive":
            return self._inventory_extreme(reverse=True)

        if intent == "check_low_stock":
            return self._low_stock_summary()

        if intent == "check_total_stock":
            return self._total_stock_summary()

        if intent == "list_matching_products" and product_name:
            return self._list_matching_products(product_name)

        product = self.inventory_service.search_product(product_name or "")

        if product:
            return self._format_product_response(product, intent, message)

        return self._no_product_response(message)
