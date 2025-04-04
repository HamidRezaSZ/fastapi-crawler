from fastapi import FastAPI

from app.routers import products

app = FastAPI(title="Discounted Men's Clothing Products Scraper API")

app.include_router(products.router)
