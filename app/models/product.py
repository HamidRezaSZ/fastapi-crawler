from pydantic import BaseModel


class Product(BaseModel):
    name: str
    original_price: str
    discounted_price: str
    discount_percent: float
    purchase_url: str
    image_url: str
    store: str
    category: str
