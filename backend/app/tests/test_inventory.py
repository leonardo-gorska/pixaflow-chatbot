import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Product
from app.services.inventory_service import InventoryService


# Setup test database
TEST_DATABASE_URL = "sqlite:///./test_inventory.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    # Add test data
    test_products = [
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
    ]
    session.add_all(test_products)
    session.commit()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_search_existing_product(db_session):
    """Test searching for an existing product."""
    inventory_service = InventoryService(db_session)
    
    # Search for existing product
    product = inventory_service.search_product("arroz")
    
    assert product is not None
    assert product.name == "Arroz Camil 5kg"
    assert product.price == 29.90
    assert product.quantity == 18


def test_search_nonexistent_product(db_session):
    """Test searching for a product that doesn't exist."""
    inventory_service = InventoryService(db_session)
    
    # Search for non-existent product
    product = inventory_service.search_product("chocolate")
    
    assert product is None


def test_search_product_case_insensitive(db_session):
    """Test that product search is case-insensitive."""
    inventory_service = InventoryService(db_session)
    
    # Search with different cases
    product_lower = inventory_service.search_product("arroz")
    product_upper = inventory_service.search_product("ARROZ")
    product_mixed = inventory_service.search_product("ArRoZ")
    
    assert product_lower is not None
    assert product_upper is not None
    assert product_mixed is not None
    
    assert product_lower.name == product_upper.name == product_mixed.name


def test_search_product_partial_match(db_session):
    """Test that product search works with partial matches."""
    inventory_service = InventoryService(db_session)
    
    # Search with partial name
    product = inventory_service.search_product("feijão")
    
    assert product is not None
    assert "feijão" in product.name.lower()


def test_get_all_products(db_session):
    """Test retrieving all products."""
    inventory_service = InventoryService(db_session)
    
    products = inventory_service.get_all_products()
    
    assert len(products) == 2
    assert products[0].name == "Arroz Camil 5kg"
    assert products[1].name == "Feijão Carioca Kicaldo 1kg"


def test_get_product_by_exact_name(db_session):
    """Test getting a product by exact name."""
    inventory_service = InventoryService(db_session)
    
    product = inventory_service.get_product_by_name("Arroz Camil 5kg")
    
    assert product is not None
    assert product.name == "Arroz Camil 5kg"
    assert product.price == 29.90


def test_get_product_by_exact_name_not_found(db_session):
    """Test getting a product by exact name when it doesn't exist."""
    inventory_service = InventoryService(db_session)
    
    product = inventory_service.get_product_by_name("Produto Inexistente")
    
    assert product is None
