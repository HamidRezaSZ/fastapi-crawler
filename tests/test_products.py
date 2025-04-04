from fastapi.testclient import TestClient

from app.main import app
from app.models.product import Product

client = TestClient(app)

mock_product = Product(
    name="Mock Jacket",
    original_price="$100.00",
    discounted_price="$75.00",
    discount_percent=25.0,
    purchase_url="https://zara.com/mock-jacket",
    image_url="https://zara.com/images/mock.jpg",
    store="zara",
    category="jacket",
)


def test_get_discounted_products(monkeypatch):
    def mock_scraper():
        return [mock_product]

    from app.services import zara_scraper

    # TODO: Use the real api instead of mocking

    monkeypatch.setattr(zara_scraper, "scrape_zara_discounted_products", mock_scraper)

    response = client.get("/discounted-products")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Mock Jacket"
    assert data[0]["discount_percent"] == 25.0
