from typing import List

from playwright.sync_api import sync_playwright

from app.models.product import Product


def scrape_zara_discounted_products() -> List[Product]:
    products = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(
            "https://www.zara.com/us/en/man-all-products-l7465.html", timeout=60000
        )
        page.wait_for_timeout(5000)  # Wait for JS content to load

        items = page.query_selector_all("div.product-grid-product")

        for item in items:
            try:
                name = item.query_selector("a.name").inner_text().strip()
                url = item.query_selector("a.name").get_attribute("href")
                purchase_url = f"https://www.zara.com{url}"

                image_url = item.query_selector("img").get_attribute("src")

                original_price_el = item.query_selector("span.old-price")
                discounted_price_el = item.query_selector("span.price__amount-current")

                if not original_price_el or not discounted_price_el:
                    continue

                original_price = original_price_el.inner_text().strip()
                discounted_price = discounted_price_el.inner_text().strip()

                orig = float(original_price.replace("$", "").strip())
                disc = float(discounted_price.replace("$", "").strip())
                discount_percent = round((orig - disc) / orig * 100, 2)

                products.append(
                    Product(
                        name=name,
                        original_price=original_price,
                        discounted_price=discounted_price,
                        discount_percent=discount_percent,
                        purchase_url=purchase_url,
                        image_url=image_url,
                        store="zara",
                        category=guess_category_from_name(name),
                    )
                )
            except Exception as e:
                print(f"Error scraping an item: {e}")
                continue

        browser.close()
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
