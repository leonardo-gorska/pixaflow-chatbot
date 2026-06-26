import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch
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


@patch('app.services.chat_service.GeminiService')
def test_chat_endpoint_success(mock_gemini, client):
    """Test the chat endpoint with a valid message using mocked Gemini."""
    # Mock the intent extraction
    mock_gemini_instance = Mock()
    mock_gemini_instance.extract_intent_and_product.return_value = {
        "intent": "search_product",
        "product": "arroz"
    }
    mock_gemini_instance.format_response_with_fallback.return_value = "Sim! Temos Arroz Camil 5kg. Preço: R$29.90. Quantidade: 18 unidades."
    mock_gemini.return_value = mock_gemini_instance
    
    response = client.post(
        "/api/chat",
        json={"message": "Tem arroz?"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["answer"] is not None
    assert len(data["answer"]) > 0


@patch('app.services.chat_service.GeminiService')
def test_chat_endpoint_empty_message(mock_gemini, client):
    """Test the chat endpoint with an empty message using mocked Gemini."""
    mock_gemini_instance = Mock()
    mock_gemini_instance.extract_intent_and_product.return_value = {
        "intent": "general",
        "product": None
    }
    mock_gemini_instance.format_no_product_response.return_value = "Como posso ajudar você hoje?"
    mock_gemini.return_value = mock_gemini_instance
    
    response = client.post(
        "/api/chat",
        json={"message": ""}
    )
    
    # Should still return 200, but with a response
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data


@patch('app.services.chat_service.GeminiService')
def test_chat_endpoint_nonexistent_product(mock_gemini, client):
    """Test the chat endpoint asking about a non-existent product using mocked Gemini."""
    mock_gemini_instance = Mock()
    mock_gemini_instance.extract_intent_and_product.return_value = {
        "intent": "search_product",
        "product": "chocolate"
    }
    mock_gemini_instance.format_no_product_response.return_value = "Desculpe, não encontrei esse produto no nosso estoque."
    mock_gemini.return_value = mock_gemini_instance
    
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


@patch('app.services.chat_service.GeminiService')
def test_chat_endpoint_quantity_query(mock_gemini, client):
    """Test the chat endpoint asking about quantity using mocked Gemini."""
    mock_gemini_instance = Mock()
    mock_gemini_instance.extract_intent_and_product.return_value = {
        "intent": "check_quantity",
        "product": "arroz"
    }
    mock_gemini_instance.format_response_with_fallback.return_value = "Temos 18 unidades de Arroz Camil 5kg em estoque."
    mock_gemini.return_value = mock_gemini_instance
    
    response = client.post(
        "/api/chat",
        json={"message": "Quantos arroz tem?"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["answer"] is not None


@patch('app.services.chat_service.GeminiService')
def test_chat_endpoint_price_query(mock_gemini, client):
    """Test the chat endpoint asking about price using mocked Gemini."""
    mock_gemini_instance = Mock()
    mock_gemini_instance.extract_intent_and_product.return_value = {
        "intent": "check_price",
        "product": "feijão"
    }
    mock_gemini_instance.format_response_with_fallback.return_value = "O Feijão Carioca Kicaldo 1kg custa R$8.90."
    mock_gemini.return_value = mock_gemini_instance
    
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
