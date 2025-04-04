from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.models.product import Product
from app.utils.logger import logger

ZARA_MEN_SALE_URL = "https://www.zara.com/us/en/man-all-products-l7465.html"


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


def scrape_zara_discounted_products() -> List[Product]:
    """
    Scrap Zara discounted mens clothing products using Selenium.
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

    try:
        driver = initialize_driver()

        driver.get(ZARA_MEN_SALE_URL)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product"))
        )

        products = []
        items = driver.find_elements(By.CLASS_NAME, "product")

        for item in items:
            try:
                name = item.find_element(By.CLASS_NAME, "product-name").text.strip()
                url = f"https://www.zara.com{item.find_element(By.TAG_NAME, 'a').get_attribute('href')}"
                image_url = item.find_element(By.TAG_NAME, 'img').get_attribute('src')
                original_price = item.find_element(
                    By.CLASS_NAME, "original-price"
                ).text.strip()
                discounted_price = item.find_element(
                    By.CLASS_NAME, "discounted-price"
                ).text.strip()

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
                        store="zara",
                        category=guess_category_from_name(name),
                    )
                )
            except Exception as e:
                logger.error(f"Error processing product in Zara: {e}")
                continue

    except Exception as e:
        logger.error(f"Error scraping Zara page: {e}")
    finally:
        driver.quit()

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
