import time
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.models.product import Product
from app.utils.logger import logger

AMAZON_MEN_SALE_URL = "https://www.amazon.com/s?i=specialty-aps&bbn=16225019011&rh=n%3A7141123011%2Cn%3A16225019011%2Cn%3A1040658"


def initialize_driver() -> webdriver.Chrome:
    """
    Initialize the Selenium WebDriver with Chrome options
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    logger.info("Selenium WebDriver initialized")
    return driver


def scrape_amazon_discounted_products() -> List[Product]:
    """
    Scrape Amazon discounted men's clothing products using Selenium.
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
    driver = initialize_driver()

    try:
        driver.get(AMAZON_MEN_SALE_URL)

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "s-main-slot"))
        )

        products = []

        items = driver.find_elements(By.CSS_SELECTOR, "div[data-asin]")

        for item in items:
            try:
                name = item.find_element(By.CLASS_NAME, "a-text-normal").text
                url = f"https://www.amazon.com{item.find_element(By.TAG_NAME, 'a').get_attribute('href')}"
                image_url = item.find_element(By.TAG_NAME, "img").get_attribute("src")

                original_price_el = item.find_element(By.CLASS_NAME, "a-price-whole")
                discounted_price_el = item.find_element(By.CLASS_NAME, "a-price-symbol")

                if not original_price_el or not discounted_price_el:
                    continue

                original_price = original_price_el.text
                discounted_price = discounted_price_el.text

                orig = float(original_price.replace("$", "").replace(",", "").strip())
                disc = float(discounted_price.replace("$", "").replace(",", "").strip())
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

        return products

    except Exception as e:
        logger.error(f"Error scraping Amazon products: {e}")
        return []

    finally:
        driver.quit()


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
