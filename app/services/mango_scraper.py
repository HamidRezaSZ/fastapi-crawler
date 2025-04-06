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

MANGO_MEN_SALE_URL = os.getenv('MANGO_MEN_SALE_URL')
CACHE_KEY = os.getenv("MANGO_CACHE_KEY")
SELENIUM_URL = os.getenv("SELENIUM_URL")


def initialize_driver() -> webdriver.Chrome:
    """
    Initialize the Selenium WebDriver with Chrome options
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument('--disable-extensions')
    options.add_argument('--blink-settings=imagesEnabled=false')
    driver = webdriver.Remote(
        command_executor=SELENIUM_URL,
        options=options,
    )
    logger.info("Selenium WebDriver initialized")
    return driver


async def scrape_mango_discounted_products() -> List[Product]:
    """
    Scrap Mango discounted mens clothing products using Selenium.
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
    products = []

    cached = await get_cache(CACHE_KEY)
    if cached:
        return [Product(**p) for p in json.loads(cached)]

    try:
        driver = initialize_driver()
        driver.get(MANGO_MEN_SALE_URL)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "virtual-list"))
        )

        items = driver.find_elements(By.CLASS_NAME, "virtual-item")

        for item in items:
            try:
                name = item.find_element(
                    By.CLASS_NAME, "ProductTitle_productTitle___cM9O"
                ).text.strip()
                url = item.find_element(By.TAG_NAME, 'a').get_attribute('href')
                image_url = item.find_element(By.TAG_NAME, 'img').get_attribute('src')
                original_price = item.find_element(
                    By.CLASS_NAME, "SinglePrice_center__mfcM3"
                ).text.strip()
                discounted_price = (
                    item.find_elements(By.CLASS_NAME, "SinglePrice_finalPrice__CGsuZ")[
                        -1
                    ].text.strip()
                    if item.find_elements(
                        By.CLASS_NAME, "SinglePrice_finalPrice__CGsuZ"
                    )
                    else original_price
                )

                orig = float(original_price.replace(" TL", "").replace(",", "").strip())
                disc = float(
                    discounted_price.replace(" TL", "").replace(",", "").strip()
                )
                discount_percent = round((orig - disc) / orig * 100, 2)

                if discount_percent < 0:
                    continue

                products.append(
                    Product(
                        name=name,
                        original_price=original_price,
                        discounted_price=discounted_price,
                        discount_percent=discount_percent,
                        purchase_url=url,
                        image_url=image_url,
                        store="mango",
                        category=guess_category_from_name(name),
                    )
                )
            except Exception as e:
                logger.error(f"Error processing product in Mango: {e}")
                continue

    except Exception as e:
        logger.error(f"Error scraping Mango page: {e}")
    finally:
        driver.quit()

    await set_cache(CACHE_KEY, [p.dict() for p in products])
    return products


def guess_category_from_name(name: str) -> str:
    name_lower = name.lower()
    if "ceket" in name_lower:
        return "jacket"
    if "gömlek" in name_lower:
        return "shirt"
    if "pantolon" in name_lower:
        return "pants"
    if "sweatshirt" in name_lower:
        return "sweatshirt"
    if "mont" in name_lower:
        return "coat"
    return "other"
