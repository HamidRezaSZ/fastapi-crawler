from typing import List

import requests
from bs4 import BeautifulSoup

from app.models.product import Product
from app.utils.logger import logger

AMAZON_MEN_SALE_URL = "https://www.amazon.com/s?i=specialty-aps&bbn=16225019011&rh=n%3A7141123011%2Cn%3A16225019011%2Cn%3A1040658"


def scrape_amazon_discounted_products() -> List[Product]:
    """
    Scrap Amazon discounted mens clothing products
    Returns a list of Product objects with the following attributes:
    - name: str
    - original_price: str
    - discounted_price: str
    - discount_percent: float
    - purchase_url: str
    - image_url: str
    - store: str
    - category: str
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    try:
        response = requests.get(AMAZON_MEN_SALE_URL, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Amazon page: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")

    products = []

    try:
        items = soup.find_all("div", {"data-asin": True})
        for item in items:
            try:
                name = item.find("span", class_="a-text-normal").get_text(strip=True)
                url = f"https://www.amazon.com{item.find('a')['href']}"
                image_url = item.find("img")["src"]
                original_price_el = item.find("span", class_="a-price-whole")
                discounted_price_el = item.find("span", class_="a-price-symbol")

                if not original_price_el or not discounted_price_el:
                    continue

                original_price = original_price_el.get_text(strip=True)
                discounted_price = discounted_price_el.get_text(strip=True)

                orig = float(original_price.replace("$", "").strip())
                disc = float(discounted_price.replace("$", "").strip())
                discount_percent = round((orig - disc) / orig * 100, 2)

                products.append(
                    Product(
                        name=name,
                        original_price=original_price,
                        discounted_price=discounted_price,
                        discount_percent=discount_percent,
                        purchase_url=url,
                        image_url=image_url,
                        store="amazon",
                        category=guess_category_from_name(name),
                    )
                )
            except Exception as e:
                logger.error(f"Error processing Amazon product: {e}")
                continue
    except Exception as e:
        logger.error(f"Error scraping Amazon products: {e}")

    return products


def guess_category_from_name(name: str) -> str:
    name_lower = name.lower()
    if "jacket" in name_lower:
        return "jacket"
    if "shirt" in name_lower or "tee" in name_lower:
        return "shirt"
    if "pants" in name_lower or "trouser" in name_lower:
        return "pants"
    if "hoodie" in name_lower:
        return "hoodie"
    return "other"
