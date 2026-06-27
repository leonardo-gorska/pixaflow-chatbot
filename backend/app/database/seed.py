from app.database.database import SessionLocal, init_db
from app.database.models import Product


SAMPLE_PRODUCTS = [
    {
        "id": 1,
        "name": "Arroz Camil 5kg",
        "description": "Arroz branco tipo 1",
        "price": 29.90,
        "quantity": 18,
        "category": "Grãos",
    },
    {
        "id": 2,
        "name": "Feijão Carioca Kicaldo 1kg",
        "description": "Feijão carioca tradicional",
        "price": 8.90,
        "quantity": 40,
        "category": "Grãos",
    },
    {
        "id": 3,
        "name": "Leite Integral Itambé 1L",
        "description": "Leite integral pasteurizado",
        "price": 6.50,
        "quantity": 12,
        "category": "Laticínios",
    },
    {
        "id": 4,
        "name": "Café Pilão Tradicional 500g",
        "description": "Café torrado e moído",
        "price": 17.80,
        "quantity": 9,
        "category": "Bebidas",
    },
    {
        "id": 5,
        "name": "Macarrão Renata Espaguete 500g",
        "description": "Macarrão de trigo",
        "price": 5.20,
        "quantity": 25,
        "category": "Massas",
    },
    {
        "id": 6,
        "name": "Açúcar União Refinado 1kg",
        "description": "Açúcar refinado",
        "price": 4.90,
        "quantity": 31,
        "category": "Açúcar",
    },
    {
        "id": 7,
        "name": "Óleo de Soja Soya 900ml",
        "description": "Óleo vegetal de soja",
        "price": 8.50,
        "quantity": 15,
        "category": "Óleos",
    },
    {
        "id": 8,
        "name": "Farinha de Trigo Dona Benta 1kg",
        "description": "Farinha de trigo enriquecida",
        "price": 6.20,
        "quantity": 22,
        "category": "Farinhas",
    },
]


def seed_database():
    init_db()

    db = SessionLocal()
    try:
        for product_data in SAMPLE_PRODUCTS:
            product = db.query(Product).filter(Product.id == product_data["id"]).first()
            if not product:
                product = db.query(Product).filter(Product.name == product_data["name"]).first()
            if product:
                for field, value in product_data.items():
                    setattr(product, field, value)
            else:
                db.add(Product(**product_data))

        db.commit()
        print(f"Database seeded/updated with {len(SAMPLE_PRODUCTS)} products.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
