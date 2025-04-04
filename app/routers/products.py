from typing import List, Optional

from fastapi import APIRouter, Query

from app.models.product import Product
from app.services.amazon_scraper import scrape_amazon_discounted_products
from app.services.zara_scraper import scrape_zara_discounted_products

router = APIRouter()


@router.get(
    "/discounted-products",
    response_model=List[Product],
    summary="Get discounted men's clothing products",
    description="""
    This endpoint returns a list of discounted men's clothing products from various stores such as Zara and Amazon.
    You can filter the products by store, category, and minimum discount percentage.
    The response includes product details such as name, price, discount, and image URL.
    """,
)
def get_discounted_products(
    store: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    min_discount: Optional[float] = Query(None),
):
    all_products: List[Product] = []

    try:
        if not store or store == "zara":
            all_products.extend(scrape_zara_discounted_products())

        if not store or store == "zara":
            all_products.extend(scrape_amazon_discounted_products())

        # TODO: Make filtering more efficient
        if category:
            all_products = [
                p for p in all_products if p.category.lower() == category.lower()
            ]

        if min_discount:
            all_products = [
                p for p in all_products if p.discount_percent >= min_discount
            ]

        if store:
            all_products = [p for p in all_products if p.store.lower() == store.lower()]

    except Exception as e:
        print(f"Error showing products: {e}")
        return []

    return all_products
