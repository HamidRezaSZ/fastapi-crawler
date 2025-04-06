# FastAPI-Based E-commerce Crawler

This project is a **FastAPI-based backend service** that crawls selected e-commerce websites (Zara, Amazon, Mango) to retrieve **discounted men's clothing** products. It exposes this data through a **JSON API**, supports filtering, pagination, and is designed to scale with async scraping and Redis caching.

---

## Design Decisions

- **FastAPI** is used for its performance, automatic OpenAPI documentation, and native async support.
- **Selenium** powers web scraping for dynamic pages like Zara and Amazon.
- **Redis** caches results to reduce repeated scraping and improve performance.
- **Asyncio** allows concurrent scraping across multiple stores for faster response times.
- **Pydantic models** ensure clean, typed, and validated API responses.
- **Logging** is implemented via the built-in `logging` module.
- Easily extendable architecture — just drop a new scraper function and route.

---

## Project Structure

```plaintext
app/
├── main.py                # FastAPI app and API setup
├── models/                
│   └── product.py         # Pydantic model for products
├── routers/                
│   └── products.py        # Product API with filters, pagination
├── services/
│   ├── amazon_scraper.py  # Amazon scraping logic (Selenium)
│   ├── zara_scraper.py    # Zara scraping logic (Selenium)
│   └── mango_scraper.py   # Mango scraping logic (Selenium)
│   └── redis_cache.py           # Redis caching helpers
├── utils/
│   ├── logger.py          # Logger setup
tests/
└── test_products.py       # Basic tests
Dockerfile                 # Dockerfile for containerization
docker-compose.yml         # Multi-service config (API + Redis + Chrome)
README.md                  # You're here
requirements.txt           # Python dependencies
```

---

## Installation

### 1. Clone and install dependencies
```bash
git clone https://github.com/HamidRezaSZ/fastapi-crawler.git
cd fastapi-crawler
pip install -r requirements.txt
```

### 2. ChromeDriver setup (if running locally)
Ensure your system has Chrome and the correct version of [ChromeDriver](https://chromedriver.chromium.org/). Place the binary in your PATH or configure Selenium to use a custom path.

---

## Docker Setup (Recommended)

### 1. Build and run with Docker Compose
```bash
docker-compose up --build
```

This starts:
- FastAPI app at [http://localhost:8000](http://localhost:8000)
- Redis cache
- Chrome (headless, for Selenium)

### 2. View docs
Visit [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger UI.

---

## Sample API Requests

### 1. Get all discounted products
```bash
curl "http://localhost:8000/discounted-products"
```

### 2. Filter by store and discount
```bash
curl "http://localhost:8000/discounted-products?store=zara&min_discount=20"
```

### 3. Filter by category
```bash
curl "http://localhost:8000/discounted-products?category=shirt&min_discount=30"
```

### 4. Paginate
```bash
curl "http://localhost:8000/discounted-products?page=2&page_size=5"
```

---

## Caching with Redis

The API caches results per store using Redis to reduce scraping load and improve speed. Cached data expires after 1 hour by default. You can adjust TTL in `app/utils/cache.py`.

No setup needed — Redis is included in Docker Compose.

---

## Testing

Run the tests using:
```bash
pytest tests/test_products.py
```

Make sure Chrome/Redis are accessible during testing or mock them.

---

## Technologies Used

- **FastAPI**
- **Selenium**
- **Redis**
- **Docker & Docker Compose**
- **Pydantic**
