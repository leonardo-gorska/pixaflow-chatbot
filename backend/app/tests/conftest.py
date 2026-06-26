import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Product
from app.database.database import get_db
from app.main import app


# Setup test database
TEST_DATABASE_URL = "sqlite:///:memory:"
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


@pytest.fixture
def client(db_session):
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    from fastapi.testclient import TestClient
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
