import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Product
from app.database.database import get_db
from app.main import app


# Setup test database
TEST_DATABASE_URL = "sqlite:///./test_chat.db"
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
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


def test_chat_endpoint_success(client):
    """Test the chat endpoint with a valid message."""
    response = client.post(
        "/api/chat",
        json={"message": "Tem arroz?"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["answer"] is not None
    assert len(data["answer"]) > 0


def test_chat_endpoint_empty_message(client):
    """Test the chat endpoint with an empty message."""
    response = client.post(
        "/api/chat",
        json={"message": ""}
    )
    
    # Should still return 200, but with a response
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data


def test_chat_endpoint_nonexistent_product(client):
    """Test the chat endpoint asking about a non-existent product."""
    response = client.post(
        "/api/chat",
        json={"message": "Tem chocolate?"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["answer"] is not None
    # Should indicate product not found
    assert "não" in data["answer"].lower() or "desculpe" in data["answer"].lower()


def test_chat_endpoint_quantity_query(client):
    """Test the chat endpoint asking about quantity."""
    response = client.post(
        "/api/chat",
        json={"message": "Quantos arroz tem?"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["answer"] is not None


def test_chat_endpoint_price_query(client):
    """Test the chat endpoint asking about price."""
    response = client.post(
        "/api/chat",
        json={"message": "Quanto custa o feijão?"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["answer"] is not None


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "status" in data
    assert data["status"] == "running"


def test_health_endpoint(client):
    """Test the health check endpoint with component status."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "components" in data
    assert "api" in data["components"]
    assert "database" in data["components"]
    assert "gemini" in data["components"]


def test_get_all_products(client):
    """Test the GET /products endpoint."""
    response = client.get("/api/products")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_product_by_id(client):
    """Test the GET /products/{id} endpoint."""
    response = client.get("/api/products/1")
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["id"] == 1
    assert "name" in data


def test_get_product_by_id_not_found(client):
    """Test GET /products/{id} with non-existent ID."""
    response = client.get("/api/products/999")
    
    assert response.status_code == 404
