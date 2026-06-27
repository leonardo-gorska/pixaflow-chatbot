from app.services.inventory_service import InventoryService


def test_search_existing_product(db_session):
    inventory_service = InventoryService(db_session)

    product = inventory_service.search_product("arroz")

    assert product is not None
    assert product.name == "Arroz Camil 5kg"
    assert product.to_dict()["price"] == 29.90
    assert product.quantity == 18


def test_search_nonexistent_product(db_session):
    inventory_service = InventoryService(db_session)

    product = inventory_service.search_product("chocolate")

    assert product is None


def test_search_product_case_insensitive(db_session):
    inventory_service = InventoryService(db_session)

    product_lower = inventory_service.search_product("arroz")
    product_upper = inventory_service.search_product("ARROZ")
    product_mixed = inventory_service.search_product("ArRoZ")

    assert product_lower is not None
    assert product_upper is not None
    assert product_mixed is not None
    assert product_lower.name == product_upper.name == product_mixed.name


def test_search_product_ignores_accents_and_simple_plural(db_session):
    inventory_service = InventoryService(db_session)

    product = inventory_service.search_product("cafés")

    assert product is not None
    assert product.name == "Café Pilão Tradicional 500g"


def test_search_product_partial_match(db_session):
    inventory_service = InventoryService(db_session)

    product = inventory_service.search_product("feijão")

    assert product is not None
    assert "Feijão" in product.name


def test_get_all_products(db_session):
    inventory_service = InventoryService(db_session)

    products = inventory_service.get_all_products()

    assert len(products) == 4
    assert products[0].name == "Arroz Camil 5kg"
    assert products[1].name == "Feijão Carioca Kicaldo 1kg"


def test_get_product_by_exact_name(db_session):
    inventory_service = InventoryService(db_session)

    product = inventory_service.get_product_by_name("Arroz Camil 5kg")

    assert product is not None
    assert product.name == "Arroz Camil 5kg"
    assert product.to_dict()["price"] == 29.90


def test_get_product_by_exact_name_not_found(db_session):
    inventory_service = InventoryService(db_session)

    product = inventory_service.get_product_by_name("Produto Inexistente")

    assert product is None
