from app.database.database import SessionLocal, init_db
from app.database.models import Product


def seed_database():
    init_db()
    
    db = SessionLocal()
    
    # Check if database is already seeded
    existing_products = db.query(Product).count()
    if existing_products > 0:
        print("Database already seeded.")
        return
    
    sample_products = [
        Product(
            name="Arroz Camil 5kg",
            description="Arroz integral premium",
            price=29.90,
            quantity=18,
            category="Grãos"
        ),
        Product(
            name="Feijão Carioca Kicaldo 1kg",
            description="Feijão carioca tradicional",
            price=8.90,
            quantity=40,
            category="Grãos"
        ),
        Product(
            name="Leite Integral Itambé 1L",
            description="Leite integral pasteurizado",
            price=6.50,
            quantity=12,
            category="Laticínios"
        ),
        Product(
            name="Café Pilão Tradicional 500g",
            description="Café torrado e moído",
            price=17.80,
            quantity=9,
            category="Bebidas"
        ),
        Product(
            name="Macarrão Renata Espaguete 500g",
            description="Macarrão de trigo",
            price=5.20,
            quantity=25,
            category="Massas"
        ),
        Product(
            name="Açúcar União Refinado 1kg",
            description="Açúcar cristal refinado",
            price=4.90,
            quantity=31,
            category="Açúcar"
        ),
        Product(
            name="Óleo de Soja Soya 900ml",
            description="Óleo vegetal",
            price=8.50,
            quantity=15,
            category="Óleos"
        ),
        Product(
            name="Farinha de Trigo Dona Benta 1kg",
            description="Farinha de trigo enriquecida",
            price=6.20,
            quantity=22,
            category="Farinhas"
        ),
    ]
    
    db.add_all(sample_products)
    db.commit()
    print(f"Database seeded with {len(sample_products)} products.")


if __name__ == "__main__":
    seed_database()
