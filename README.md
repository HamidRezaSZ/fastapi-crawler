# FastAPI-Based E-commerce Crawler

This project is a FastAPI-based backend service that crawls selected e-commerce websites (such as Zara and Amazon) to retrieve discounted men's clothing products. The scraped data is exposed via a clean and flexible JSON API. The project uses **Selenium** for web scraping, **FastAPI** for the API layer, and **Pydantic models** for structured data.

## Design Decisions

- **FastAPI** was chosen for building the API layer due to its asynchronous support, automatic OpenAPI docs, and excellent performance.
- **Selenium** is used for scraping Amazon and Zara as both sites require rendering JavaScript and dynamic content loading. This ensures that the content is fully rendered before data extraction.
- **Pydantic** models are used for data validation and structure to ensure that the data returned by the scraping process is consistent and easy to work with.
- **Logging** is implemented using Python's standard logging library for better traceability and debugging.
- The project is designed to be easily extendable to other e-commerce websites by adding new scraping functions and endpoints.

## Project Structure

```plaintext
app/
├── main.py                # FastAPI application
├── models/                
│   └── product.py         # Pydantic models for products
├── routers/                
│   └── products.py         # Get and return the scraped products API
├── services/
│   └── amazon_scraper.py         # Scraping logic for Amazon
│   └── zara_scraper.py         # Scraping logic for Zara
├── utils/
│   └── logger.py          # Logger configuration
tests/
└── test_products.py       # Basic tests for the API
Dockerfile                 # Dockerfile for containerization
README.md                  # Project documentation
requirements.txt           # Project dependencies
```

