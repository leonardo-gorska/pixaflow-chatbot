import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_settings
from app.database.database import get_db
from app.database.models import Base, Product
from app.main import app


TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def disable_gemini_for_tests(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    test_products = [
        Product(
            name="Arroz Camil 5kg",
            description="Arroz branco tipo 1",
            price=29.90,
            quantity=18,
            category="Grãos",
        ),
        Product(
            name="Feijão Carioca Kicaldo 1kg",
            description="Feijão carioca tradicional",
            price=8.90,
            quantity=40,
            category="Grãos",
        ),
        Product(
            name="Café Pilão Tradicional 500g",
            description="Café torrado e moído",
            price=17.80,
            quantity=9,
            category="Bebidas",
        ),
        Product(
            name="Leite Integral Itambé 1L",
            description="Leite integral pasteurizado",
            price=6.50,
            quantity=12,
            category="Laticínios",
        ),
    ]
    session.add_all(test_products)
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
