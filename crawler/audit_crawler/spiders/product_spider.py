# product_spider.py - Spider for crawling websites and extracting product information

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urlparse
import logging
import re

class ProductSpider(CrawlSpider):
    """
    Spider for crawling websites and extracting product information.
    This spider focuses specifically on identifying and extracting data from product pages.
    """
    
    name = "product_spider"
    
    def __init__(self, start_urls=None, allowed_domains=None, *args, **kwargs):
        """
        Initialize the spider with the provided configuration.
        
        Args:
            start_urls (str): Comma-separated list of URLs to start crawling from
            allowed_domains (str): Comma-separated list of domains to restrict the crawl to
        """
        super(ProductSpider, self).__init__(*args, **kwargs)
        
        # Set start URLs
        if start_urls:
            self.start_urls = [url.strip() for url in start_urls.split(',')]
        else:
            self.start_urls = ['https://example.com']
        
        # Set allowed domains
        if allowed_domains:
            self.allowed_domains = [domain.strip() for domain in allowed_domains.split(',')]
        else:
            # Extract domains from start URLs
            self.allowed_domains = [urlparse(url).netloc for url in self.start_urls]
        
        # Common patterns for identifying product pages
        self.product_url_patterns = [
            r'/product/',
            r'/item/',
            r'/p/',
            r'[pP]roduct[-_]?[dD]etail',
            r'[pP]roduct[-_]?[pP]age'
        ]
        
        # Compile product URL patterns
        self.compiled_product_url_patterns = [re.compile(pattern) for pattern in self.product_url_patterns]
        
        # Define rules for link extraction
        self.rules = (
            # Rule for product pages
            Rule(LinkExtractor(allow=self.product_url_patterns), callback='parse_product'),
            # Rule for following links
            Rule(LinkExtractor(allow_domains=self.allowed_domains), follow=True),
        )
        
        # Initialize the rules
        self._compile_rules()
        
        logging.info(f"Spider initialized with start URLs: {self.start_urls}")
        logging.info(f"Spider initialized with allowed domains: {self.allowed_domains}")
    
    def parse_start_url(self, response):
        """
        Parse the start URL.
        
        Args:
            response: The response object
            
        Returns:
            Generator of scraped items or requests
        """
        # Check if the start URL is a product page
        if self._is_product_page(response):
            return self.parse_product(response)
        
        # Log the start URL
        logging.info(f"Crawling started at: {response.url}")
        
        # Follow the rules for link extraction
        return self._parse_response(response, self.parse_start_url, cb_kwargs={}, follow=True)
    
    def parse_product(self, response):
        """
        Parse a product page and extract product information.
        
        Args:
            response: The response object
            
        Returns:
            dict: Extracted product information
        """
        # Log the product URL
        logging.info(f"Found product page: {response.url}")
        
        # Extract product information
        product = {
            'url': response.url,
            'page_type': 'product',
            'crawl_timestamp': self._get_timestamp()
        }
        
        # Extract product name
        product['name'] = self._extract_product_name(response)
        
        # Extract product price
        product['price'] = self._extract_product_price(response)
        
        # Extract product description
        product['description'] = self._extract_product_description(response)
        
        # Extract product SKU
        product['sku'] = self._extract_product_sku(response)
        
        # Extract product images
        product['images'] = self._extract_product_images(response)
        
        # Extract meta information
        product['meta'] = {
            'title': response.css('title::text').get(),
            'meta_description': response.css('meta[name="description"]::attr(content)').get(),
            'meta_keywords': response.css('meta[name="keywords"]::attr(content)').get()
        }
        
        # Log the extracted product
        logging.info(f"Extracted product: {product['name']}")
        
        return product
    
    def _is_product_page(self, response):
        """
        Check if the response is a product page.
        
        Args:
            response: The response object
            
        Returns:
            bool: True if the response is a product page, False otherwise
        """
        # Check URL patterns
        for pattern in self.compiled_product_url_patterns:
            if pattern.search(response.url):
                return True
        
        # Check if the page has product indicators
        product_indicators = [
            # Common product page elements
            response.css('div.product'),
            response.css('div.product-detail'),
            response.css('#product'),
            response.css('.product-page'),
            response.css('.product-info'),
            
            # Common product data elements
            response.css('[itemprop="product"]'),
            response.css('[itemtype*="Product"]'),
            response.css('.price'),
            response.css('[itemprop="price"]'),
            response.css('.add-to-cart'),
            response.css('.buy-now')
        ]
        
        # If any indicators are found, it's likely a product page
        if any(product_indicators):
            return True
        
        return False
    
    def _extract_product_name(self, response):
        """
        Extract the product name from the response.
        
        Args:
            response: The response object
            
        Returns:
            str: Product name or None if not found
        """
        # Common selectors for product names
        selectors = [
            'h1.product-title::text',
            'h1[itemprop="name"]::text',
            'h1::text',
            '.product-name::text',
            '.product-title::text',
            '[itemprop="name"]::text'
        ]
        
        # Try each selector
        for selector in selectors:
            name = response.css(selector).get()
            if name:
                return name.strip()
        
        return None
    
    def _extract_product_price(self, response):
        """
        Extract the product price from the response.
        
        Args:
            response: The response object
            
        Returns:
            str: Product price or None if not found
        """
        # Common selectors for product prices
        selectors = [
            '.price::text',
            '[itemprop="price"]::text',
            '.product-price::text',
            '.price-value::text',
            '.current-price::text',
            '.sale-price::text',
            '#price::text'
        ]
        
        # Try each selector
        for selector in selectors:
            price = response.css(selector).get()
            if price:
                return price.strip()
        
        return None
    
    def _extract_product_description(self, response):
        """
        Extract the product description from the response.
        
        Args:
            response: The response object
            
        Returns:
            str: Product description or None if not found
        """
        # Common selectors for product descriptions
        selectors = [
            '.product-description',
            '[itemprop="description"]',
            '.description',
            '#description',
            '.product-details',
            '.details'
        ]
        
        # Try each selector
        for selector in selectors:
            description = response.css(selector).get()
            if description:
                # Clean up the HTML
                return description.strip()
        
        return None
    
    def _extract_product_sku(self, response):
        """
        Extract the product SKU from the response.
        
        Args:
            response: The response object
            
        Returns:
            str: Product SKU or None if not found
        """
        # Common selectors for product SKUs
        selectors = [
            '[itemprop="sku"]::text',
            '.product-sku::text',
            '.sku::text',
            '#sku::text',
            '.product-id::text',
            '[itemprop="productID"]::text'
        ]
        
        # Try each selector
        for selector in selectors:
            sku = response.css(selector).get()
            if sku:
                return sku.strip()
        
        return None
    
    def _extract_product_images(self, response):
        """
        Extract the product images from the response.
        
        Args:
            response: The response object
            
        Returns:
            list: List of product image URLs
        """
        # Common selectors for product images
        selectors = [
            '.product-image::attr(src)',
            '[itemprop="image"]::attr(src)',
            '.product img::attr(src)',
            '.product-img::attr(src)',
            '.product-photo::attr(src)',
            '.gallery img::attr(src)'
        ]
        
        images = []
        
        # Try each selector
        for selector in selectors:
            image_urls = response.css(selector).getall()
            if image_urls:
                images.extend(image_urls)
        
        return images
    
    def _get_timestamp(self):
        """
        Get the current timestamp.
        
        Returns:
            str: Current timestamp in ISO format
        """
        from datetime import datetime
        return datetime.now().isoformat()