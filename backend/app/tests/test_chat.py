def post_chat(client, message: str, history: list[dict] | None = None) -> str:
    response = client.post("/api/chat", json={"message": message, "history": history or []})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["answer"]
    return data["answer"]


def test_chat_endpoint_success(client):
    answer = post_chat(client, "Tem arroz?")

    assert "Arroz Camil 5kg" in answer
    assert "18" in answer


def test_chat_endpoint_empty_message(client):
    answer = post_chat(client, "")

    assert "Olá" in answer


def test_chat_endpoint_nonexistent_product(client):
    answer = post_chat(client, "Tem chocolate?")

    assert "Não encontrei" in answer
    assert "lista completa" in answer


def test_chat_endpoint_quantity_query_with_plural_and_accent(client):
    answer = post_chat(client, "Quantos cafés tem?")

    assert "9" in answer
    assert "Café Pilão" in answer


def test_chat_endpoint_list_matching_product(client):
    answer = post_chat(client, "Quais cafés tem?")

    assert "Café Pilão" in answer
    assert "R$ 17,80" in answer


def test_chat_endpoint_price_query(client):
    answer = post_chat(client, "Quanto custa o feijão?")

    assert "Feijão Carioca" in answer
    assert "R$ 8,90" in answer


def test_chat_endpoint_price_followup_uses_previous_product(client):
    history = [
        {"role": "user", "content": "Tem café?"},
        {"role": "assistant", "content": "Sim, temos Café Pilão Tradicional 500g."},
    ]

    answer = post_chat(client, "Quanto custa?", history=history)

    assert "Café Pilão" in answer
    assert "R$ 17,80" in answer


def test_chat_endpoint_affirmative_followup_lists_products(client):
    history = [
        {"role": "user", "content": "Tem chocolate?"},
        {
            "role": "assistant",
            "content": 'Não encontrei esse item. Se quiser, pergunte "Quais produtos vocês vendem?" para ver a lista completa.',
        },
    ]

    answer = post_chat(client, "Sim", history=history)

    assert "Temos" in answer
    assert "produtos no estoque" in answer
    assert "Arroz Camil" in answer


def test_chat_endpoint_hours_query(client):
    answer = post_chat(client, "Qual o horário de funcionamento?")

    assert "segunda a sexta" in answer
    assert "8h" in answer


def test_chat_endpoint_location_query(client):
    answer = post_chat(client, "Qual o endereço?")

    assert "Rua do Mercado" in answer


def test_chat_endpoint_delivery_query(client):
    answer = post_chat(client, "Vocês entregam?")

    assert "entregas" in answer
    assert "Centro" in answer


def test_chat_endpoint_contact_query(client):
    answer = post_chat(client, "Qual o telefone de contato?")

    assert "WhatsApp" in answer
    assert "3333-0000" in answer


def test_chat_endpoint_categories_query(client):
    answer = post_chat(client, "Quais categorias vocês têm?")

    assert "Grãos" in answer
    assert "Bebidas" in answer


def test_chat_endpoint_cheapest_product_query(client):
    answer = post_chat(client, "Qual o produto mais barato?")

    assert "mais barato" in answer
    assert "Leite Integral" in answer


def test_chat_endpoint_most_expensive_product_query(client):
    answer = post_chat(client, "Qual o produto mais caro?")

    assert "mais caro" in answer
    assert "Arroz Camil" in answer


def test_chat_endpoint_low_stock_query(client):
    answer = post_chat(client, "Tem algum produto acabando?")

    assert "menor estoque" in answer
    assert "Café Pilão" in answer


def test_chat_endpoint_total_stock_query(client):
    answer = post_chat(client, "Quantas unidades no total tem no estoque?")

    assert "79 unidades" in answer


def test_chat_endpoint_returns_query(client):
    answer = post_chat(client, "Vocês fazem troca?")

    assert "troca" in answer
    assert "comprovante" in answer


def test_chat_endpoint_help_order_query(client):
    answer = post_chat(client, "Como peço alguma coisa?")

    assert "iFood" in answer
    assert "PixaFlow Mercado" in answer


def test_chat_endpoint_short_which_question_lists_products(client):
    answer = post_chat(client, "Quais?")

    assert "Arroz Camil" in answer
    assert "Café Pilão" in answer


def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "components" in data
    assert "api" in data["components"]
    assert "database" in data["components"]
    assert "gemini" in data["components"]


def test_get_all_products(client):
    response = client.get("/api/products")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 4


def test_get_product_by_id(client):
    response = client.get("/api/products/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "name" in data


def test_get_product_by_id_not_found(client):
    response = client.get("/api/products/999")

    assert response.status_code == 404
