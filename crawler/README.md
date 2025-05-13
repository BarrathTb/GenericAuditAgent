# Crawler Component

The Crawler component is responsible for crawling websites and extracting product information. It is built using the Scrapy framework.

## Structure

```
crawler/
├── audit_crawler/       # Scrapy project
│   ├── spiders/         # Spider definitions
│   │   ├── __init__.py  # Package initialization
│   │   └── generic_spider.py  # Main spider for crawling
│   ├── __init__.py      # Package initialization
│   └── settings.py      # Scrapy settings
└── scrapy.cfg           # Scrapy configuration
```

## Generic Spider

The `generic_spider.py` file contains the main spider for crawling websites. It is a configurable spider that can be used to crawl any website and extract product information based on the provided selectors.

### Configuration Options

The spider can be configured with the following parameters:

- `start_urls`: Comma-separated list of URLs to start crawling from
- `allowed_domains`: Comma-separated list of domains to restrict the crawl to
- `product_url_patterns`: JSON string of regex patterns to identify product URLs
- `product_page_selectors`: JSON string of CSS selectors to identify product pages
- `product_name_selectors`: JSON string of CSS selectors to extract product names
- `product_price_selectors`: JSON string of CSS selectors to extract product prices
- `product_description_selectors`: JSON string of CSS selectors to extract product descriptions
- `product_sku_selectors`: JSON string of CSS selectors to extract product SKUs
- `product_image_selectors`: JSON string of CSS selectors to extract product images
- `custom_fields`: JSON string of custom fields to extract

### Usage

The spider can be run using the Scrapy command-line interface:

```bash
cd crawler
scrapy crawl generic_spider -a start_urls=https://example.com -a allowed_domains=example.com
```

Or it can be run programmatically from the main application:

```python
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from audit_crawler.spiders.generic_spider import GenericSpider

# Get Scrapy settings
settings = get_project_settings()

# Create a crawler process
process = CrawlerProcess(settings)

# Configure the spider
spider = GenericSpider(
    start_urls='https://example.com',
    allowed_domains='example.com',
    product_url_patterns='["/product/", "/item/"]',
    product_name_selectors='["h1.product-title::text", "h1::text"]'
)

# Start the crawler
process.crawl(spider)
process.start()
```

## Customization

The crawler component can be customized by:

1. Modifying the `settings.py` file to adjust Scrapy settings
2. Creating new spiders in the `spiders` directory
3. Adding middleware and pipelines to the Scrapy project

For more information on Scrapy, see the [official documentation](https://docs.scrapy.org/).
