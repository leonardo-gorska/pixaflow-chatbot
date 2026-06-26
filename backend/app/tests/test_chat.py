import pytest
from unittest.mock import Mock, patch


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


@patch('app.services.chat_service.GeminiService')
def test_fallback_on_gemini_failure(mock_gemini, client):
    """Test that fallback works when Gemini fails during intent extraction."""
    mock_gemini_instance = Mock()
    # Simulate Gemini failure during intent extraction
    mock_gemini_instance.extract_intent_and_product.side_effect = Exception("Gemini API error")
    mock_gemini_instance.format_no_product_response.return_value = "Desculpe, não encontrei esse produto no nosso estoque."
    mock_gemini.return_value = mock_gemini_instance
    
    response = client.post(
        "/api/chat",
        json={"message": "Tem arroz?"}
    )
    
    # Should still return 200 with fallback response
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["answer"] is not None
