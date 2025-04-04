from fastapi import FastAPI

from app.routers import products

app = FastAPI(
    title="Discounted Men's Clothing Products Scraper API",
    description="This API retrieves discounted men's clothing products from stores like Zara and Amazon.",
    version="1.0.0",
)

app.include_router(products.router)
