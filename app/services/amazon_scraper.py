import json
import os
import time
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.models.product import Product
from app.services.redis_cache import get_cache, set_cache
from app.utils.logger import logger

AMAZON_MEN_SALE_URL = os.environ.get('AMAZON_MEN_SALE_URL')
CACHE_KEY = os.environ.get("AMAZON_CACHE_KEY")
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


async def scrape_amazon_discounted_products() -> List[Product]:
    """
    Scrape Amazon discounted men's clothing products using Selenium.

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
        page = 1
        driver.get(AMAZON_MEN_SALE_URL)

        while len(products) == 0 and page <= 3:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "s-main-slot"))
            )

            items = driver.find_elements(By.CSS_SELECTOR, "div[data-asin]")

            for item in items:
                try:
                    if (
                        item.get_attribute("data-index")
                        and item.get_attribute("data-index") <= "5"
                    ) or (
                        not item.find_elements(
                            By.CLASS_NAME, "s-title-instructions-style"
                        )
                        or item.find_elements(
                            By.CLASS_NAME, "s-title-instructions-style"
                        )[0].text.strip()
                        == ""
                    ):
                        continue

                    name = (
                        item.find_element(By.CLASS_NAME, "s-title-instructions-style")
                        .find_element(By.TAG_NAME, "span")
                        .text.strip()
                    )

                    url = item.find_element(
                        By.CLASS_NAME, 'a-link-normal'
                    ).get_attribute('href')
                    image_url = item.find_element(
                        By.CLASS_NAME, "s-image"
                    ).get_attribute("src")

                    discounted_price_whole = item.find_element(
                        By.CLASS_NAME, "a-price-whole"
                    ).text.strip()

                    discounted_price_fraction = item.find_element(
                        By.CLASS_NAME, "a-price-fraction"
                    ).text.strip()

                    original_price_el = item.find_elements(
                        By.CLASS_NAME, "a-text-price"
                    )
                    discounted_price = (
                        discounted_price_whole + "." + discounted_price_fraction
                    )

                    price_symbol = (
                        item.find_elements(By.CLASS_NAME, "a-price-symbol")[
                            -1
                        ].text.strip()
                        if item.find_elements(By.CLASS_NAME, "a-price-symbol")
                        else "$"
                    )

                    original_price = (
                        original_price_el[-1].text.strip().replace(price_symbol, "")
                        if original_price_el and original_price_el[-1].text.strip()
                        else 0
                    )

                    if original_price == 0:
                        continue

                    orig = float(original_price)
                    disc = float(discounted_price)
                    discount_percent = round((orig - disc) / orig * 100, 2)

                    if discount_percent <= 0:
                        continue

                    products.append(
                        Product(
                            name=name,
                            original_price=f"{price_symbol}{original_price}",
                            discounted_price=f"{price_symbol}{discounted_price}",
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

            page += 1
            if driver.find_elements(By.CLASS_NAME, "s-pagination-next"):
                driver.find_elements(By.CLASS_NAME, "s-pagination-next")[0].click()
            time.sleep(2)

    except Exception as e:
        logger.error(f"Error scraping Amazon products: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.error(f"Error quitting the driver: {e}")

    await set_cache(CACHE_KEY, [p.dict() for p in products])
    return products


def guess_category_from_name(name: str) -> str:
    """Guess product category based on product name."""
    name_lower = name.lower()
    if "jacket" in name_lower:
        return "jacket"
    if "shirt" in name_lower or "tee" in name_lower:
        return "shirt"
    if "pants" in name_lower or "trouser" in name_lower:
        return "pants"
    if "hoodie" in name_lower:
        return "hoodie"
    if "socks" in name_lower:
        return "socks"
    if "shorts" in name_lower:
        return "shorts"
    return "other"
