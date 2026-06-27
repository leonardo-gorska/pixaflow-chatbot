from difflib import SequenceMatcher
from typing import List, Optional
import re
import unicodedata

from sqlalchemy.orm import Session

from app.database.models import Product


class InventoryService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def normalize_text(text: str) -> str:
        text = text or ""
        text = unicodedata.normalize("NFD", text.lower())
        text = "".join(char for char in text if unicodedata.category(char) != "Mn")
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @classmethod
    def singularize_token(cls, token: str) -> str:
        irregular = {
            "cafes": "cafe",
            "feijoes": "feijao",
            "graos": "grao",
            "paes": "pao",
        }
        if token in irregular:
            return irregular[token]
        if token.endswith("oes") and len(token) > 4:
            return token[:-3] + "ao"
        if token.endswith("is") and len(token) > 3:
            return token[:-2] + "il"
        if token.endswith("es") and len(token) > 4:
            return token[:-2]
        if token.endswith("s") and len(token) > 3:
            return token[:-1]
        return token

    @classmethod
    def normalize_query(cls, query: str) -> str:
        normalized = cls.normalize_text(query)
        tokens = [cls.singularize_token(token) for token in normalized.split()]
        return " ".join(tokens)

    def _product_search_text(self, product: Product) -> str:
        return self.normalize_query(
            " ".join(
                filter(
                    None,
                    [
                        product.name,
                        product.description,
                        product.category,
                    ],
                )
            )
        )

    def search_products(self, query: str) -> List[Product]:
        """
        Search products by normalized name, description or category.
        Handles accents, case and simple Portuguese plurals.
        """
        query_normalized = self.normalize_query(query)
        if not query_normalized:
            return []

        query_tokens = set(query_normalized.split())
        scored_matches = []

        for product in self.db.query(Product).all():
            product_name = self.normalize_query(product.name)
            product_text = self._product_search_text(product)
            product_name_tokens = set(product_name.split())
            product_tokens = set(product_text.split())

            if query_normalized in product_name or product_name in query_normalized:
                score = 100
            else:
                name_overlap = len(query_tokens & product_name_tokens)
                text_overlap = len(query_tokens & product_tokens)
                score = (name_overlap * 10) + text_overlap

            if score > 0:
                scored_matches.append((score, product))

        scored_matches.sort(key=lambda item: item[0], reverse=True)
        return [product for _, product in scored_matches]

    def search_product(self, query: str) -> Optional[Product]:
        """
        Search for the best product match by name, description or category.
        """
        products = self.search_products(query)
        if products:
            return products[0]

        query_normalized = self.normalize_query(query)
        if not query_normalized:
            return None

        best_match = None
        best_ratio = 0.62

        for product in self.db.query(Product).all():
            product_name = self.normalize_query(product.name)
            ratio = SequenceMatcher(None, query_normalized, product_name).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = product

        return best_match

    def get_all_products(self) -> List[Product]:
        return self.db.query(Product).all()

    def get_product_by_name(self, name: str) -> Optional[Product]:
        normalized_name = self.normalize_query(name)
        for product in self.db.query(Product).all():
            if self.normalize_query(product.name) == normalized_name:
                return product
        return None
