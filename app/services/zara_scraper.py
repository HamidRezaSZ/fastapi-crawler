import json
import os
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.models.product import Product
from app.services.redis_cache import get_cache, set_cache
from app.utils.logger import logger

ZARA_MEN_SALE_URL = os.environ.get('ZARA_MEN_SALE_URL')
CACHE_KEY = os.environ.get("ZARA_CACHE_KEY")
SELENIUM_URL = os.environ.get("SELENIUM_URL")


def initialize_driver() -> webdriver.Chrome:
    """Initialize the Selenium WebDriver with Chrome options."""
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument('--disable-extensions')
    options.add_argument('--blink-settings=imagesEnabled=false')

    if os.environ.get("USE_REMOTE_DRIVER", "false").lower() == "true":
        driver = webdriver.Remote(
            command_executor=SELENIUM_URL,
            options=options,
        )
    else:
        driver = webdriver.Chrome(options=options)

    logger.info("Selenium WebDriver initialized")
    return driver


async def scrape_zara_discounted_products() -> List[Product]:
    """
    Scrape Zara discounted men's clothing products using Selenium.

    Returns:
        List[Product]: A list of Product objects with attributes:
            - name: str
            - original_price: str
            - discounted_price: str
            - discount_percent: float
            - purchase_url: str
            - image_url: str
            - store: str
            - category: str
    """
    products = []
    driver = None

    cached = await get_cache(CACHE_KEY)
    if cached:
        return [Product(**p) for p in json.loads(cached)]

    try:
        driver = initialize_driver()
        driver.get(ZARA_MEN_SALE_URL)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "onetrust-reject-all-handler"))
            )
            driver.find_element(By.ID, "onetrust-reject-all-handler").click()
        except Exception:
            pass

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "product-grid__product-list")
            )
        )

        items = driver.find_elements(By.CLASS_NAME, "_product")

        for item in items:
            try:
                name = item.find_element(
                    By.CLASS_NAME, "product-grid-product-info__name"
                ).text.strip()

                url = item.find_element(
                    By.CLASS_NAME, 'product-grid-product-info__name'
                ).get_attribute('href')

                image_url = item.find_element(
                    By.CLASS_NAME, 'media-image__image'
                ).get_attribute('src')

                price_elements = item.find_elements(By.CLASS_NAME, "money-amount__main")
                original_price = (
                    price_elements[-2].text.strip()
                    if len(price_elements) >= 2
                    else "$ 0"
                )

                discounted_price = (
                    price_elements[-1].text.strip()
                    if price_elements
                    else original_price
                )

                if not original_price or not discounted_price:
                    continue

                orig = float(original_price.replace("$ ", "").strip())
                disc = float(discounted_price.replace("$ ", "").strip())
                discount_percent = round((orig - disc) / orig * 100, 2)

                products.append(
                    Product(
                        name=name,
                        original_price=original_price,
                        discounted_price=discounted_price,
                        discount_percent=discount_percent,
                        purchase_url=url,
                        image_url=image_url,
                        store="zara",
                        category=guess_category_from_name(name),
                    )
                )
            except Exception as e:
                logger.error(f"Error processing Zara product: {e}")
                continue

    except Exception as e:
        logger.error(f"Error scraping Zara products: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.error(f"Error quitting the driver: {e}")

    await set_cache(CACHE_KEY, [p.dict() for p in products])
    return products


def guess_category_from_name(name: str) -> str:
    """Guess product category based on product name keywords."""
    name_lower = name.lower()
    if "jacket" in name_lower:
        return "jacket"
    if "shirt" in name_lower:
        return "shirt"
    if "pants" in name_lower or "trousers" in name_lower:
        return "pants"
    if "hoodie" in name_lower or "sweatshirt" in name_lower:
        return "hoodie"
    return "other"
