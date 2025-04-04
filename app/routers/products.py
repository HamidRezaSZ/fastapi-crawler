from typing import List, Optional

from fastapi import APIRouter, Query

from app.models.product import Product
from app.services.zara_scraper import scrape_zara_discounted_products

router = APIRouter()


@router.get("/discounted-products", response_model=List[Product])
def get_discounted_products(
    store: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    min_discount: Optional[float] = Query(None),
):
    all_products: List[Product] = []

    if not store or store == "zara":
        all_products.extend(scrape_zara_discounted_products())

    # TODO: Add Amazon scraper

    # TODO: Make filtering more efficient
    if category:
        all_products = [
            p for p in all_products if p.category.lower() == category.lower()
        ]

    if min_discount:
        all_products = [p for p in all_products if p.discount_percent >= min_discount]

    if store:
        all_products = [p for p in all_products if p.store.lower() == store.lower()]

    return all_products
