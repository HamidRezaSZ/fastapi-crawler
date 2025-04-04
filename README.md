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

# Install Dependencies

Install the required Python packages using pip:
```bash
pip install -r requirements.txt
```

# Setup ChromeDriver (for Selenium)

Download the appropriate version of ChromeDriver that matches your Chrome version.
Ensure that the chromedriver binary is available in your PATH or provide the path in the code.

# Run the Project

1. Run the FastAPI server using uvicorn:
```bash
uvicorn app.main:app --reload
```
This starts the FastAPI application locally on port 8000 by default. The OpenAPI docs will be available at http://127.0.0.1:8000/docs.

2. Test the API:
You can test the API by calling the GET /discounted-products endpoint. The API allows the following optional query parameters:

- store: Filter by store (e.g., zara, amazon).
- category: Filter by clothing type (e.g., shirt, pants).
- min_discount: Minimum discount percentage (e.g., 20).
- page: The page of results to return
- page_size: The number of results per page

# Sample API Requests

1. Fetch all discounted products:
```bash
curl -X 'GET' 'http://127.0.0.1:8000/discounted-products'
```
2. Fetch discounted products from Zara with at least a 20% discount:
```bash
curl -X 'GET' 'http://127.0.0.1:8000/discounted-products?store=zara&min_discount=20'

```
3. Fetch discounted shirts with at least a 30% discount:
```bash
curl -X 'GET' 'http://127.0.0.1:8000/discounted-products?category=shirt&min_discount=30'
```

# Docker Setup

To run the application in Docker, use the following steps:
1. Build the Docker image:
```bash
docker build -t fastapi-crawler .
```
2. Run the Docker container:
```bash
docker run -d -p 8000:8000 fastapi-crawler
```
The API will be available at http://localhost:8000.

# Testing

Basic test cases are included to validate the core functionality of the API.

To run the tests:
```bash
pytest tests/test_products.py
```