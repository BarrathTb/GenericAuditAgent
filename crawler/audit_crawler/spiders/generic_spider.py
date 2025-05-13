# generic_spider.py - Generic spider for crawling websites and extracting product information

import json
import re
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urlparse
import logging

class GenericSpider(CrawlSpider):
    """
    Generic spider for crawling websites and extracting product information.
    This spider can be configured to crawl any website and extract product information
    based on the provided selectors.
    """
    
    name = "generic_spider"
    
    def __init__(self, start_urls=None, allowed_domains=None, product_url_patterns=None,
                 product_page_selectors=None, product_name_selectors=None,
                 product_price_selectors=None, product_description_selectors=None,
                 product_sku_selectors=None, product_image_selectors=None,
                 product_specs_selectors=None, custom_fields=None, crawl_limit=None, *args, **kwargs):
        """
        Initialize the spider with the provided configuration.
        
        Args:
            start_urls (str): Comma-separated list of URLs to start crawling from
            allowed_domains (str): Comma-separated list of domains to restrict the crawl to
            product_url_patterns (str): JSON string of regex patterns to identify product URLs
            product_page_selectors (str): JSON string of CSS selectors to identify product pages
            product_name_selectors (str): JSON string of CSS selectors to extract product names
            product_price_selectors (str): JSON string of CSS selectors to extract product prices
            product_description_selectors (str): JSON string of CSS selectors to extract product descriptions
            product_sku_selectors (str): JSON string of CSS selectors to extract product SKUs
            product_image_selectors (str): JSON string of CSS selectors to extract product images
            product_specs_selectors (str): JSON string of CSS selectors to extract product specifications
            custom_fields (str): JSON string of custom fields to extract
        """
        super(GenericSpider, self).__init__(*args, **kwargs)
        
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
        
        # Set product URL patterns
        if product_url_patterns:
            try:
                self.product_url_patterns = json.loads(product_url_patterns)
            except json.JSONDecodeError:
                self.product_url_patterns = [r'/product/', r'/item/', r'[pP]roduct[-_]?[dD]etail']
                logging.warning(f"Invalid JSON for product_url_patterns: {product_url_patterns}")
        else:
            self.product_url_patterns = [r'/product/', r'/item/', r'[pP]roduct[-_]?[dD]etail']
        
        # Set product page selectors
        if product_page_selectors:
            try:
                self.product_page_selectors = json.loads(product_page_selectors)
            except json.JSONDecodeError:
                self.product_page_selectors = ['div.product', 'div.product-detail', '#product']
                logging.warning(f"Invalid JSON for product_page_selectors: {product_page_selectors}")
        else:
            self.product_page_selectors = ['div.product', 'div.product-detail', '#product']
        
        # Set product name selectors
        if product_name_selectors:
            try:
                self.product_name_selectors = json.loads(product_name_selectors)
            except json.JSONDecodeError:
                self.product_name_selectors = ['h1.product-title::text', 'h1[itemprop="name"]::text', 'h1::text']
                logging.warning(f"Invalid JSON for product_name_selectors: {product_name_selectors}")
        else:
            self.product_name_selectors = ['h1.product-title::text', 'h1[itemprop="name"]::text', 'h1::text']
        
        # Set product price selectors
        if product_price_selectors:
            try:
                self.product_price_selectors = json.loads(product_price_selectors)
            except json.JSONDecodeError:
                self.product_price_selectors = ['.price::text', '[itemprop="price"]::text', '.product-price::text']
                logging.warning(f"Invalid JSON for product_price_selectors: {product_price_selectors}")
        else:
            self.product_price_selectors = ['.price::text', '[itemprop="price"]::text', '.product-price::text']
        
        # Set product description selectors
        if product_description_selectors:
            try:
                self.product_description_selectors = json.loads(product_description_selectors)
            except json.JSONDecodeError:
                self.product_description_selectors = ['.product-description', '[itemprop="description"]', '.description']
                logging.warning(f"Invalid JSON for product_description_selectors: {product_description_selectors}")
        else:
            self.product_description_selectors = ['.product-description', '[itemprop="description"]', '.description']
        
        # Set product SKU selectors
        if product_sku_selectors:
            try:
                self.product_sku_selectors = json.loads(product_sku_selectors)
            except json.JSONDecodeError:
                self.product_sku_selectors = ['[itemprop="sku"]::text', '.product-sku::text', '.sku::text']
                logging.warning(f"Invalid JSON for product_sku_selectors: {product_sku_selectors}")
        else:
            self.product_sku_selectors = ['[itemprop="sku"]::text', '.product-sku::text', '.sku::text']
        
        # Set product image selectors
        if product_image_selectors:
            try:
                self.product_image_selectors = json.loads(product_image_selectors)
            except json.JSONDecodeError:
                self.product_image_selectors = ['.product-image::attr(src)', '[itemprop="image"]::attr(src)', '.product img::attr(src)']
                logging.warning(f"Invalid JSON for product_image_selectors: {product_image_selectors}")
        else:
            self.product_image_selectors = ['.product-image::attr(src)', '[itemprop="image"]::attr(src)', '.product img::attr(src)']
            
        # Set product specifications selectors
        if product_specs_selectors:
            try:
                self.product_specs_selectors = json.loads(product_specs_selectors)
            except json.JSONDecodeError:
                self.product_specs_selectors = ['.product-specs', '.specifications', 'table.specs', '.additional-attributes']
                logging.warning(f"Invalid JSON for product_specs_selectors: {product_specs_selectors}")
        else:
            self.product_specs_selectors = ['.product-specs', '.specifications', 'table.specs', '.additional-attributes']
        
        # Set custom fields
        if custom_fields:
            try:
                self.custom_fields = json.loads(custom_fields)
            except json.JSONDecodeError:
                self.custom_fields = {}
                logging.warning(f"Invalid JSON for custom_fields: {custom_fields}")
        else:
            self.custom_fields = {}
            
        # Set crawl limit
        if crawl_limit:
            try:
                self.crawl_limit = int(crawl_limit)
                logging.info(f"Crawl limit set to {self.crawl_limit} pages")
            except ValueError:
                self.crawl_limit = None
                logging.warning(f"Invalid crawl limit: {crawl_limit}")
        else:
            self.crawl_limit = None
            
        # Initialize page counter
        self.pages_crawled = 0
        
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
        
        # Increment page counter
        self.pages_crawled += 1
        logging.info(f"Pages crawled: {self.pages_crawled}")
        
        # Check if we've reached the crawl limit
        if self.crawl_limit and self.pages_crawled >= self.crawl_limit:
            logging.info(f"Reached crawl limit of {self.crawl_limit} pages. Stopping crawl.")
            return []
        
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
        
        # Increment page counter
        self.pages_crawled += 1
        logging.info(f"Pages crawled: {self.pages_crawled}")
        
        # Check if we've reached the crawl limit
        if self.crawl_limit and self.pages_crawled >= self.crawl_limit:
            logging.info(f"Reached crawl limit of {self.crawl_limit} pages. Stopping crawl after processing this product.")
        
        # Extract product information
        product = {
            'url': response.url,
            'page_type': 'product',
            'crawl_timestamp': self.get_timestamp()
        }
        
        # Extract product name
        product['name'] = self._extract_first(response, self.product_name_selectors)
        
        # Extract product price
        product['price'] = self._extract_first(response, self.product_price_selectors)
        
        # Extract product description
        product['description'] = self._extract_first(response, self.product_description_selectors, is_text=False)
        
        # Extract product SKU
        product['sku'] = self._extract_first(response, self.product_sku_selectors)
        
        # Extract product images
        product['images'] = self._extract_all(response, self.product_image_selectors)
        
        # Extract product specifications
        product['specs'] = self._extract_first(response, self.product_specs_selectors, is_text=False)
        
        # Extract custom fields
        for field_name, selector in self.custom_fields.items():
            # If selector contains multiple selectors separated by commas, split them
            if ',' in selector:
                selector_list = [s.strip() for s in selector.split(',')]
                product[field_name] = self._extract_first(response, selector_list)
            else:
                product[field_name] = self._extract_first(response, [selector])
        
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
        
        # Check page selectors
        for selector in self.product_page_selectors:
            if response.css(selector):
                return True
        
        # Check if the page has product name and price
        has_name = any(response.css(selector) for selector in self.product_name_selectors)
        has_price = any(response.css(selector) for selector in self.product_price_selectors)
        
        if has_name and has_price:
            return True
        
        return False
    
    def _extract_first(self, response, selectors, is_text=True):
        """
        Extract the first matching element using the provided selectors.
        
        Args:
            response: The response object
            selectors (list): List of CSS selectors
            is_text (bool): Whether to extract text or the element itself
            
        Returns:
            str: Extracted text or None if not found
        """
        for selector in selectors:
            if is_text:
                result = response.css(selector).get()
            else:
                # For elements like descriptions, extract the HTML
                result = response.css(selector).get()
                if result:
                    # Clean up the HTML
                    result = result.strip()
            
            if result:
                return result
        
        return None
    
    def _extract_all(self, response, selectors):
        """
        Extract all matching elements using the provided selectors.
        
        Args:
            response: The response object
            selectors (list): List of CSS selectors
            
        Returns:
            list: List of extracted elements
        """
        results = []
        
        for selector in selectors:
            items = response.css(selector).getall()
            if items:
                results.extend(items)
        
        return results
    
    def get_timestamp(self):
        """
        Get the current timestamp.
        
        Returns:
            str: Current timestamp in ISO format
        """
        from datetime import datetime
        return datetime.now().isoformat()