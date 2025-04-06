import unittest

from app.models.product import Product
from app.services.amazon_scraper import scrape_amazon_discounted_products
from app.services.mango_scraper import scrape_mango_discounted_products
from app.services.zara_scraper import scrape_zara_discounted_products


class TestScraping(unittest.TestCase):

    def test_scrape_zara_discounted_products(self) -> None:
        """Test the Zara scraping function with real data"""
        products = scrape_zara_discounted_products()

        self.assertGreater(
            len(products), 0, "No products found on Zara's discounted page"
        )

        for product in products:
            self.assertIsInstance(product, Product)
            self.assertIsInstance(product.name, str)
            self.assertIsInstance(product.original_price, str)
            self.assertIsInstance(product.discounted_price, str)
            self.assertIsInstance(product.discount_percent, float)
            self.assertIsInstance(product.purchase_url, str)
            self.assertIsInstance(product.image_url, str)

    def test_scrape_amazon_discounted_products(self) -> None:
        """Test the Amazon scraping function with real data"""
        products = scrape_amazon_discounted_products()

        self.assertGreater(
            len(products), 0, "No products found on Amazon's discounted page"
        )

        for product in products:
            self.assertIsInstance(product, Product)
            self.assertIsInstance(product.name, str)
            self.assertIsInstance(product.original_price, str)
            self.assertIsInstance(product.discounted_price, str)
            self.assertIsInstance(product.discount_percent, float)
            self.assertIsInstance(product.purchase_url, str)
            self.assertIsInstance(product.image_url, str)

    def test_scrape_mango_discounted_products(self) -> None:
        """Test the Mango scraping function with real data"""
        products = scrape_mango_discounted_products()

        self.assertGreater(
            len(products), 0, "No products found on Mango's discounted page"
        )

        for product in products:
            self.assertIsInstance(product, Product)
            self.assertIsInstance(product.name, str)
            self.assertIsInstance(product.original_price, str)
            self.assertIsInstance(product.discounted_price, str)
            self.assertIsInstance(product.discount_percent, float)
            self.assertIsInstance(product.purchase_url, str)
            self.assertIsInstance(product.image_url, str)


if __name__ == "__main__":
    unittest.main()
