# extractor.py - Extract structured data from raw crawler output

import os
import json
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import re

class ProductExtractor:
    """
    Extract structured data from raw crawler output.
    This component processes the raw JSON data from the crawler and extracts
    relevant information into a structured format for analysis.
    """
    
    def __init__(self, input_dir="data/raw", output_dir="data/processed"):
        """
        Initialize the ProductExtractor.
        
        Args:
            input_dir (str): Directory containing raw crawler output files
            output_dir (str): Directory to save processed data files
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def process_file(self, filename):
        """
        Process a raw crawler output file and extract structured data.
        
        Args:
            filename (str): Name of the file to process
            
        Returns:
            str: Path to the processed output file
        """
        # Construct full input path
        input_path = os.path.join(self.input_dir, filename)
        
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"processed_{os.path.splitext(filename)[0]}_{timestamp}.json"
        output_path = os.path.join(self.output_dir, output_filename)
        
        print(f"Processing {input_path} -> {output_path}")
        
        # Load raw data
        with open(input_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # Process the data
        processed_data = self._process_data(raw_data)
        
        # Save processed data
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)
        
        print(f"Extracted {len(processed_data['products'])} products")
        
        return output_path
    
    def _process_data(self, raw_data):
        """
        Process the raw data and extract structured information.
        
        Args:
            raw_data (list): List of raw data items from the crawler
            
        Returns:
            dict: Structured data with extracted information
        """
        # Initialize result structure
        result = {
            "metadata": {
                "processed_timestamp": datetime.now().isoformat(),
                "total_pages": len(raw_data),
                "product_count": 0,
                "article_count": 0,
                "other_count": 0
            },
            "products": [],
            "articles": [],
            "other_pages": []
        }
        
        # Process each item
        for item in raw_data:
            # Skip items without a page_type
            if "page_type" not in item:
                continue
            
            # Process based on page type
            if item["page_type"] == "product":
                processed_item = self._process_product(item)
                result["products"].append(processed_item)
                result["metadata"]["product_count"] += 1
            elif item["page_type"] == "article":
                processed_item = self._process_article(item)
                result["articles"].append(processed_item)
                result["metadata"]["article_count"] += 1
            else:
                result["other_pages"].append(item)
                result["metadata"]["other_count"] += 1
        
        return result
    
    def _process_product(self, product_data):
        """
        Process a product item to extract and clean product information.
        
        Args:
            product_data (dict): Raw product data from the crawler
            
        Returns:
            dict: Processed product data
        """
        # Create a copy to avoid modifying the original
        processed = dict(product_data)
        
        # Clean product name
        if "name" in processed:
            processed["name"] = self._clean_text(processed["name"])
        
        # Clean product description
        if "description" in processed:
            processed["description"] = self._clean_text(processed["description"])
        
        # Clean price (extract numeric value)
        if "price" in processed:
            processed["price_raw"] = processed["price"]
            processed["price_numeric"] = self._extract_price(processed["price"])
        
        # Extract dimensions from specifications if available
        if "specifications" in processed:
            dimensions = self._extract_dimensions(processed["specifications"])
            if dimensions:
                processed["dimensions"] = dimensions
        
        # Add extraction metadata
        processed["extraction_timestamp"] = datetime.now().isoformat()
        
        return processed
    
    def _process_article(self, article_data):
        """
        Process an article item to extract and clean article information.
        
        Args:
            article_data (dict): Raw article data from the crawler
            
        Returns:
            dict: Processed article data
        """
        # Create a copy to avoid modifying the original
        processed = dict(article_data)
        
        # Clean article title
        if "title" in processed:
            processed["title"] = self._clean_text(processed["title"])
        
        # Clean article content
        if "content" in processed:
            processed["content"] = self._clean_text(processed["content"])
            processed["content_length"] = len(processed["content"])
            processed["word_count"] = len(processed["content"].split())
        
        # Add extraction metadata
        processed["extraction_timestamp"] = datetime.now().isoformat()
        
        return processed
    
    def _clean_text(self, text):
        """
        Clean text by removing extra whitespace, HTML tags, etc.
        
        Args:
            text (str): Text to clean
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Convert to string if not already
        text = str(text)
        
        # Remove HTML tags
        text = BeautifulSoup(text, "html.parser").get_text()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_price(self, price_text):
        """
        Extract numeric price from price text.
        
        Args:
            price_text (str): Price text (e.g., "$99.99", "€50", etc.)
            
        Returns:
            float or None: Extracted numeric price or None if not found
        """
        if not price_text:
            return None
        
        # Convert to string if not already
        price_text = str(price_text)
        
        # Extract numeric value using regex
        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        if price_match:
            try:
                return float(price_match.group().replace(',', ''))
            except ValueError:
                return None
        
        return None
    
    def _extract_dimensions(self, specifications):
        """
        Extract dimension information from product specifications.
        
        Args:
            specifications (dict): Product specifications
            
        Returns:
            dict or None: Extracted dimensions or None if not found
        """
        dimensions = {}
        dimension_keys = {
            "length": ["length", "len", "l"],
            "width": ["width", "w", "wide"],
            "height": ["height", "h", "tall"],
            "diameter": ["diameter", "dia", "φ"],
            "weight": ["weight", "wt"]
        }
        
        for spec_key, spec_value in specifications.items():
            spec_key_lower = spec_key.lower()
            
            for dim_key, aliases in dimension_keys.items():
                if any(alias in spec_key_lower for alias in aliases):
                    # Extract numeric value
                    value_match = re.search(r'[\d.]+', str(spec_value))
                    if value_match:
                        dimensions[dim_key] = {
                            "value": float(value_match.group()),
                            "unit": self._extract_unit(spec_value)
                        }
        
        return dimensions if dimensions else None
    
    def _extract_unit(self, text):
        """
        Extract unit from text.
        
        Args:
            text (str): Text containing a unit
            
        Returns:
            str or None: Extracted unit or None if not found
        """
        common_units = {
            "length": ["mm", "cm", "m", "in", "inch", "inches", "ft", "foot", "feet"],
            "weight": ["g", "kg", "lb", "lbs", "oz", "ounce", "ounces"]
        }
        
        text = str(text).lower()
        
        for category, units in common_units.items():
            for unit in units:
                if unit in text:
                    return unit
        
        return None