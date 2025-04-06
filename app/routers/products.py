import asyncio
from typing import List, Optional

from fastapi import APIRouter, Query

from app.models.product import Product
from app.services.amazon_scraper import scrape_amazon_discounted_products
from app.services.mango_scraper import scrape_mango_discounted_products
from app.services.zara_scraper import scrape_zara_discounted_products
from app.utils.logger import logger

router = APIRouter()


@router.get(
    "/discounted-products",
    response_model=List[Product],
    summary="Get discounted men's clothing products",
    description="This endpoint returns a list of discounted men's clothing products from various stores such as Zara, Amazon, and Mango.",
)
async def get_discounted_products(
    store: Optional[str] = Query(
        None, description="Filter by store (e.g., 'zara', 'amazon', 'mango')"
    ),
    category: Optional[str] = Query(
        None, description="Filter by clothing category (e.g., 'shirt', 'jacket')"
    ),
    min_discount: Optional[float] = Query(
        None, ge=0, le=100, description="Filter by minimum discount percentage (0-100%)"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
) -> List[Product]:
    """
    Get discounted products with filtering and pagination support.
    - store: Optional filter by store (zara, amazon, etc.)
    - category: Optional filter by category (shirts, jackets, etc.)
    - min_discount: Optional filter by minimum discount percentage
    - page: The page of results to return
    - page_size: The number of results per page
    """
    all_products: List[Product] = []

    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    try:
        scrape_tasks = []

        if not store or store.lower() == "zara":
            scrape_tasks.append(scrape_zara_discounted_products())
        if not store or store.lower() == "amazon":
            scrape_tasks.append(scrape_amazon_discounted_products())
        if not store or store.lower() == "mango":
            scrape_tasks.append(scrape_mango_discounted_products())

        results = await asyncio.gather(*scrape_tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Scraping error: {result}")
            else:
                all_products.extend(result)

        if category:
            all_products = [
                p for p in all_products if p.category.lower() == category.lower()
            ]
        if min_discount:
            all_products = [
                p for p in all_products if p.discount_percent >= min_discount
            ]

        return all_products[start_index:end_index]

    except Exception as e:
        logger.error(f"Error processing the request for discounted products: {e}")

    return all_products[start_index:end_index]
