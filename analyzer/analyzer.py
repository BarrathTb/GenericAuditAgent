# analyzer.py - Analyze extracted data and generate insights

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import spacy
import textstat

class ProductAnalyzer:
    """
    Analyze extracted product data and generate insights.
    This component processes the structured data from the extractor and performs
    various analyses to generate insights about the products and content.
    """
    
    def __init__(self, input_dir="data/processed", output_dir="data/analyzed"):
        """
        Initialize the ProductAnalyzer.
        
        Args:
            input_dir (str): Directory containing processed data files
            output_dir (str): Directory to save analysis results
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize NLP components
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))
        
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading spaCy model...")
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
    
    def analyze_file(self, filename):
        """
        Analyze a processed data file and generate insights.
        
        Args:
            filename (str): Name of the file to analyze
            
        Returns:
            str: Path to the analysis output file
        """
        # Construct full input path
        input_path = os.path.join(self.input_dir, filename)
        
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"analyzed_{os.path.splitext(filename)[0]}_{timestamp}.json"
        output_path = os.path.join(self.output_dir, output_filename)
        
        print(f"Analyzing {input_path} -> {output_path}")
        
        # Load processed data
        with open(input_path, 'r', encoding='utf-8') as f:
            processed_data = json.load(f)
        
        # Analyze the data
        analysis_results = self._analyze_data(processed_data)
        
        # Save analysis results
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"Analysis completed with {len(analysis_results['product_analyses'])} product analyses")
        
        return output_path
    
    def _analyze_data(self, processed_data):
        """
        Analyze the processed data and generate insights.
        
        Args:
            processed_data (dict): Processed data from the extractor
            
        Returns:
            dict: Analysis results with insights
        """
        # Initialize result structure
        result = {
            "metadata": {
                "analysis_timestamp": datetime.now().isoformat(),
                "product_count": processed_data["metadata"]["product_count"],
                "article_count": processed_data["metadata"]["article_count"]
            },
            "summary": self._generate_summary(processed_data),
            "product_analyses": [],
            "article_analyses": [],
            "content_quality_analysis": self._analyze_content_quality(processed_data),
            "seo_analysis": self._analyze_seo(processed_data)
        }
        
        # Analyze each product
        for product in processed_data["products"]:
            product_analysis = self._analyze_product(product)
            result["product_analyses"].append(product_analysis)
        
        # Analyze each article
        for article in processed_data["articles"]:
            article_analysis = self._analyze_article(article)
            result["article_analyses"].append(article_analysis)
        
        return result
    
    def _generate_summary(self, processed_data):
        """
        Generate a summary of the processed data.
        
        Args:
            processed_data (dict): Processed data from the extractor
            
        Returns:
            dict: Summary statistics and insights
        """
        products = processed_data["products"]
        articles = processed_data["articles"]
        
        # Calculate price statistics if prices are available
        price_stats = {}
        numeric_prices = [p.get("price_numeric") for p in products if p.get("price_numeric") is not None]
        
        if numeric_prices:
            price_stats = {
                "min_price": min(numeric_prices),
                "max_price": max(numeric_prices),
                "avg_price": sum(numeric_prices) / len(numeric_prices),
                "median_price": sorted(numeric_prices)[len(numeric_prices) // 2],
                "price_count": len(numeric_prices)
            }
        
        # Calculate content statistics
        product_word_counts = [len(p.get("description", "").split()) for p in products if "description" in p]
        article_word_counts = [a.get("word_count", 0) for a in articles if "word_count" in a]
        
        content_stats = {}
        if product_word_counts:
            content_stats["avg_product_description_length"] = sum(product_word_counts) / len(product_word_counts)
        
        if article_word_counts:
            content_stats["avg_article_length"] = sum(article_word_counts) / len(article_word_counts)
        
        # Identify common product categories
        categories = []
        for product in products:
            if "categories" in product:
                categories.extend(product["categories"])
        
        category_counts = {}
        for category in categories:
            if category in category_counts:
                category_counts[category] += 1
            else:
                category_counts[category] = 1
        
        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "price_statistics": price_stats,
            "content_statistics": content_stats,
            "top_categories": [{"category": cat, "count": count} for cat, count in top_categories]
        }
    
    def _analyze_product(self, product):
        """
        Analyze a single product and generate insights.
        
        Args:
            product (dict): Processed product data
            
        Returns:
            dict: Product analysis with insights
        """
        # Initialize product analysis
        analysis = {
            "product_id": product.get("sku", "unknown"),
            "product_name": product.get("name", "Unknown Product"),
            "url": product.get("url", ""),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # Analyze product description if available
        if "description" in product:
            description_analysis = self._analyze_text(product["description"])
            analysis["description_analysis"] = description_analysis
        
        # Analyze product specifications if available
        if "specifications" in product:
            spec_analysis = self._analyze_specifications(product["specifications"])
            analysis["specification_analysis"] = spec_analysis
        
        # Analyze product images if available
        if "images" in product:
            image_analysis = self._analyze_images(product["images"])
            analysis["image_analysis"] = image_analysis
        
        # Analyze pricing if available
        if "price" in product or "price_numeric" in product:
            price_analysis = self._analyze_price(product)
            analysis["price_analysis"] = price_analysis
        
        # Analyze product template structure if available
        if "template_structure" in product:
            template_analysis = self._analyze_template(product["template_structure"])
            analysis["template_analysis"] = template_analysis
        
        return analysis
    
    def _analyze_article(self, article):
        """
        Analyze a single article and generate insights.
        
        Args:
            article (dict): Processed article data
            
        Returns:
            dict: Article analysis with insights
        """
        # Initialize article analysis
        analysis = {
            "article_title": article.get("title", "Unknown Article"),
            "url": article.get("url", ""),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # Analyze article content if available
        if "content" in article:
            content_analysis = self._analyze_text(article["content"])
            analysis["content_analysis"] = content_analysis
        
        # Analyze article structure if available
        if "structure" in article:
            structure_analysis = self._analyze_article_structure(article["structure"])
            analysis["structure_analysis"] = structure_analysis
        
        return analysis
    
    def _analyze_text(self, text):
        """
        Analyze text content for readability, sentiment, and other metrics.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Text analysis results
        """
        if not text:
            return {"error": "No text provided"}
        
        # Basic text metrics
        word_count = len(text.split())
        sentence_count = len(sent_tokenize(text))
        avg_sentence_length = word_count / max(1, sentence_count)
        
        # Readability scores
        flesch_reading_ease = textstat.flesch_reading_ease(text)
        flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
        
        # Sentiment analysis (basic)
        doc = self.nlp(text)
        positive_words = ["good", "great", "excellent", "best", "superior", "quality", "reliable", "durable", "innovative"]
        negative_words = ["bad", "poor", "worst", "inferior", "cheap", "unreliable", "break", "problem", "issue"]
        
        positive_count = sum(1 for token in doc if token.text.lower() in positive_words)
        negative_count = sum(1 for token in doc if token.text.lower() in negative_words)
        
        sentiment_score = (positive_count - negative_count) / max(1, word_count) * 100
        
        # Extract key phrases (simplified)
        noun_phrases = []
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) > 1:  # Only multi-word phrases
                noun_phrases.append(chunk.text)
        
        # Get most common noun phrases
        phrase_counts = {}
        for phrase in noun_phrases:
            phrase_lower = phrase.lower()
            if phrase_lower in phrase_counts:
                phrase_counts[phrase_lower] += 1
            else:
                phrase_counts[phrase_lower] = 1
        
        top_phrases = sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": avg_sentence_length,
            "readability": {
                "flesch_reading_ease": flesch_reading_ease,
                "flesch_kincaid_grade": flesch_kincaid_grade,
                "interpretation": self._interpret_readability(flesch_reading_ease)
            },
            "sentiment": {
                "score": sentiment_score,
                "positive_word_count": positive_count,
                "negative_word_count": negative_count,
                "interpretation": self._interpret_sentiment(sentiment_score)
            },
            "key_phrases": [phrase for phrase, count in top_phrases]
        }
    
    def _interpret_readability(self, score):
        """
        Interpret Flesch Reading Ease score.
        
        Args:
            score (float): Flesch Reading Ease score
            
        Returns:
            str: Interpretation of the score
        """
        if score >= 90:
            return "Very Easy - 5th grade level"
        elif score >= 80:
            return "Easy - 6th grade level"
        elif score >= 70:
            return "Fairly Easy - 7th grade level"
        elif score >= 60:
            return "Standard - 8th-9th grade level"
        elif score >= 50:
            return "Fairly Difficult - 10th-12th grade level"
        elif score >= 30:
            return "Difficult - College level"
        else:
            return "Very Difficult - College graduate level"
    
    def _interpret_sentiment(self, score):
        """
        Interpret sentiment score.
        
        Args:
            score (float): Sentiment score
            
        Returns:
            str: Interpretation of the score
        """
        if score > 5:
            return "Very Positive"
        elif score > 2:
            return "Positive"
        elif score > -2:
            return "Neutral"
        elif score > -5:
            return "Negative"
        else:
            return "Very Negative"
    
    def _analyze_specifications(self, specifications):
        """
        Analyze product specifications.
        
        Args:
            specifications (dict): Product specifications
            
        Returns:
            dict: Specification analysis results
        """
        if not specifications:
            return {"error": "No specifications provided"}
        
        # Count specifications
        spec_count = len(specifications)
        
        # Categorize specifications
        categories = {
            "dimensions": ["length", "width", "height", "diameter", "size", "dimensions"],
            "performance": ["power", "speed", "capacity", "efficiency", "output", "performance"],
            "physical": ["weight", "material", "color", "finish"],
            "technical": ["voltage", "current", "frequency", "resistance", "temperature"]
        }
        
        categorized_specs = {category: [] for category in categories}
        uncategorized = []
        
        for key, value in specifications.items():
            key_lower = key.lower()
            categorized = False
            
            for category, keywords in categories.items():
                if any(keyword in key_lower for keyword in keywords):
                    categorized_specs[category].append({"key": key, "value": value})
                    categorized = True
                    break
            
            if not categorized:
                uncategorized.append({"key": key, "value": value})
        
        # Calculate completeness score (based on having specs in each category)
        completeness_score = sum(1 for category, specs in categorized_specs.items() if specs) / len(categories) * 100
        
        return {
            "spec_count": spec_count,
            "categorized_specs": categorized_specs,
            "uncategorized_specs": uncategorized,
            "completeness_score": completeness_score,
            "completeness_interpretation": self._interpret_completeness(completeness_score)
        }
    
    def _interpret_completeness(self, score):
        """
        Interpret specification completeness score.
        
        Args:
            score (float): Completeness score
            
        Returns:
            str: Interpretation of the score
        """
        if score >= 90:
            return "Excellent - Very comprehensive specifications"
        elif score >= 75:
            return "Good - Comprehensive specifications"
        elif score >= 50:
            return "Average - Adequate specifications"
        elif score >= 25:
            return "Below Average - Limited specifications"
        else:
            return "Poor - Very limited specifications"
    
    def _analyze_images(self, images):
        """
        Analyze product images.
        
        Args:
            images (list): List of image URLs
            
        Returns:
            dict: Image analysis results
        """
        if not images:
            return {"error": "No images provided"}
        
        # Count images
        image_count = len(images)
        
        # Analyze image URLs
        image_types = []
        for url in images:
            if "thumbnail" in url.lower() or "thumb" in url.lower() or "small" in url.lower():
                image_types.append("thumbnail")
            elif "large" in url.lower() or "zoom" in url.lower() or "big" in url.lower():
                image_types.append("large")
            else:
                image_types.append("standard")
        
        # Check for image variety
        has_thumbnails = "thumbnail" in image_types
        has_large_images = "large" in image_types
        
        return {
            "image_count": image_count,
            "image_types": {
                "thumbnail": image_types.count("thumbnail"),
                "standard": image_types.count("standard"),
                "large": image_types.count("large")
            },
            "has_thumbnails": has_thumbnails,
            "has_large_images": has_large_images,
            "image_score": self._calculate_image_score(image_count, has_thumbnails, has_large_images)
        }
    
    def _calculate_image_score(self, count, has_thumbnails, has_large_images):
        """
        Calculate an image quality score.
        
        Args:
            count (int): Number of images
            has_thumbnails (bool): Whether thumbnails are available
            has_large_images (bool): Whether large images are available
            
        Returns:
            dict: Image score and interpretation
        """
        # Base score based on count
        if count >= 5:
            base_score = 5
        elif count >= 3:
            base_score = 4
        elif count >= 2:
            base_score = 3
        elif count == 1:
            base_score = 2
        else:
            base_score = 0
        
        # Bonus for variety
        bonus = 0
        if has_thumbnails:
            bonus += 1
        if has_large_images:
            bonus += 2
        
        # Calculate final score (out of 10)
        final_score = min(10, base_score + bonus)
        
        # Interpret score
        if final_score >= 8:
            interpretation = "Excellent - Multiple high-quality images"
        elif final_score >= 6:
            interpretation = "Good - Sufficient images with some variety"
        elif final_score >= 4:
            interpretation = "Average - Basic image coverage"
        elif final_score >= 2:
            interpretation = "Below Average - Limited images"
        else:
            interpretation = "Poor - Inadequate images"
        
        return {
            "score": final_score,
            "interpretation": interpretation
        }
    
    def _analyze_price(self, product):
        """
        Analyze product pricing.
        
        Args:
            product (dict): Product data
            
        Returns:
            dict: Price analysis results
        """
        price_text = product.get("price", "")
        price_numeric = product.get("price_numeric")
        
        if not price_text and price_numeric is None:
            return {"error": "No price information provided"}
        
        # Analyze price format
        currency = None
        if price_text:
            if "$" in price_text:
                currency = "USD"
            elif "€" in price_text:
                currency = "EUR"
            elif "£" in price_text:
                currency = "GBP"
            elif "¥" in price_text:
                currency = "JPY"
            
            # Check for price formatting
            has_decimal = "." in price_text
            has_thousands_separator = "," in price_text and not price_text.endswith(",00")
        else:
            has_decimal = False
            has_thousands_separator = False
        
        return {
            "price_text": price_text,
            "price_numeric": price_numeric,
            "currency": currency,
            "formatting": {
                "has_decimal": has_decimal,
                "has_thousands_separator": has_thousands_separator
            }
        }
    
    def _analyze_template(self, template_structure):
        """
        Analyze product template structure.
        
        Args:
            template_structure (dict): Template structure data
            
        Returns:
            dict: Template analysis results
        """
        if not template_structure:
            return {"error": "No template structure provided"}
        
        # Calculate completeness score based on essential elements
        essential_elements = [
            "has_product_name",
            "has_price",
            "has_product_image",
            "has_description",
            "has_specifications",
            "has_add_to_cart"
        ]
        
        present_elements = sum(1 for element in essential_elements if template_structure.get(element, False))
        completeness_score = present_elements / len(essential_elements) * 100
        
        # Determine template quality
        if completeness_score >= 90:
            quality = "Excellent"
        elif completeness_score >= 75:
            quality = "Good"
        elif completeness_score >= 50:
            quality = "Average"
        elif completeness_score >= 25:
            quality = "Below Average"
        else:
            quality = "Poor"
        
        # Identify missing elements
        missing_elements = [element for element in essential_elements if not template_structure.get(element, False)]
        
        return {
            "completeness_score": completeness_score,
            "quality": quality,
            "missing_elements": missing_elements,
            "layout": template_structure.get("layout", "unknown"),
            "section_count": template_structure.get("section_count", 0)
        }
    
    def _analyze_article_structure(self, structure):
        """
        Analyze article structure.
        
        Args:
            structure (dict): Article structure data
            
        Returns:
            dict: Article structure analysis results
        """
        if not structure:
            return {"error": "No article structure provided"}
        
        # Calculate structure quality score
        quality_factors = {
            "has_introduction": 20,
            "has_conclusion": 20,
            "has_images": 15,
            "has_lists": 10,
            "has_tables": 10,
            "has_links": 10,
            "has_call_to_action": 15
        }
        
        quality_score = sum(weight for factor, weight in quality_factors.items() if structure.get(factor, False))
        
        # Determine structure quality
        if quality_score >= 90:
            quality = "Excellent"
        elif quality_score >= 75:
            quality = "Good"
        elif quality_score >= 50:
            quality = "Average"
        elif quality_score >= 25:
            quality = "Below Average"
        else:
            quality = "Poor"
        
        # Identify missing elements
        missing_elements = [factor for factor in quality_factors.keys() if not structure.get(factor, False)]
        
        return {
            "quality_score": quality_score,
            "quality": quality,
            "missing_elements": missing_elements,
            "heading_count": structure.get("heading_count", 0),
            "section_count": structure.get("section_count", 0)
        }
    
    def _analyze_content_quality(self, processed_data):
        """
        Analyze overall content quality.
        
        Args:
            processed_data (dict): Processed data from the extractor
            
        Returns:
            dict: Content quality analysis results
        """
        products = processed_data["products"]
        articles = processed_data["articles"]
        
        # Analyze product descriptions
        description_lengths = []
        readability_scores = []
        
        for product in products:
            if "description" in product:
                description_lengths.append(len(product["description"].split()))
                
                # Calculate readability
                readability = textstat.flesch_reading_ease(product["description"])
                readability_scores.append(readability)
        
        # Calculate averages
        avg_description_length = sum(description_lengths) / max(1, len(description_lengths))
        avg_readability = sum(readability_scores) / max(1, len(readability_scores))
        
        # Analyze content metrics if available
        content_metrics = []
        for product in products:
            if "content_metrics" in product:
                content_metrics.append(product["content_metrics"])
        
        for article in articles:
            if "content_metrics" in article:
                content_metrics.append(article["content_metrics"])
        
        # Calculate average metrics
        avg_metrics = {}
        if content_metrics:
            for key in content_metrics[0].keys():
                if key == "seo":
                    continue
                
                values = [metrics.get(key, 0) for metrics in content_metrics]
                avg_metrics[key] = sum(values) / len(values)
        
        return {
            "description_analysis": {
                "avg_length": avg_description_length,
                "length_interpretation": self._interpret_description_length(avg_description_length),
                "avg_readability": avg_readability,
                "readability_interpretation": self._interpret_readability(avg_readability)
            },
            "content_metrics": avg_metrics
        }
    
    def _interpret_description_length(self, length):
        """
        Interpret product description length.
        
        Args:
            length (float): Average description length in words
            
        Returns:
            str: Interpretation of the length
        """
        if length >= 300:
            return "Excellent - Comprehensive descriptions"
        elif length >= 200:
            return "Good - Detailed descriptions"
        elif length >= 100:
            return "Average - Adequate descriptions"
        elif length >= 50:
            return "Below Average - Brief descriptions"
        else:
            return "Poor - Very limited descriptions"
    
    def _analyze_seo(self, processed_data):
        """
        Analyze SEO aspects of the content.
        
        Args:
            processed_data (dict): Processed data from the extractor
            
        Returns:
            dict: SEO analysis results
        """
        products = processed_data["products"]
        articles = processed_data["articles"]
        
        # Count pages with SEO elements
        pages_with_meta_description = 0
        pages_with_meta_keywords = 0
        pages_with_h1 = 0
        pages_with_h2 = 0
        pages_with_alt_text = 0
        pages_with_structured_data = 0
        total_pages = 0
        
        # Analyze all pages
        for product in products:
            if "content_metrics" in product and "seo" in product["content_metrics"]:
                seo = product["content_metrics"]["seo"]
                total_pages += 1
                
                if seo.get("has_meta_description", False):
                    pages_with_meta_description += 1
                
                if seo.get("has_meta_keywords", False):
                    pages_with_meta_keywords += 1
                
                if seo.get("has_h1", False):
                    pages_with_h1 += 1
                
                if seo.get("has_h2", False):
                    pages_with_h2 += 1
                
                if seo.get("has_alt_text", False):
                    pages_with_alt_text += 1
                
                if seo.get("has_structured_data", False):
                    pages_with_structured_data += 1
        
        for article in articles:
            if "content_metrics" in article and "seo" in article["content_metrics"]:
                seo = article["content_metrics"]["seo"]
                total_pages += 1
                
                if seo.get("has_meta_description", False):
                    pages_with_meta_description += 1
                
                if seo.get("has_meta_keywords", False):
                    pages_with_meta_keywords += 1
                
                if seo.get("has_h1", False):
                    pages_with_h1 += 1
                
                if seo.get("has_h2", False):
                    pages_with_h2 += 1
                
                if seo.get("has_alt_text", False):
                    pages_with_alt_text += 1
                
                if seo.get("has_structured_data", False):
                    pages_with_structured_data += 1
        
        # Calculate percentages
        if total_pages > 0:
            meta_description_pct = pages_with_meta_description / total_pages * 100
            meta_keywords_pct = pages_with_meta_keywords / total_pages * 100
            h1_pct = pages_with_h1 / total_pages * 100
            h2_pct = pages_with_h2 / total_pages * 100
            alt_text_pct = pages_with_alt_text / total_pages * 100
            structured_data_pct = pages_with_structured_data / total_pages * 100
            
            # Calculate overall SEO score
            seo_score = (
                meta_description_pct * 0.25 +
                h1_pct * 0.25 +
                alt_text_pct * 0.2 +
                h2_pct * 0.1 +
                meta_keywords_pct * 0.1 +
                structured_data_pct * 0.1
            )
            
            # Interpret SEO score
            if seo_score >= 90:
                seo_quality = "Excellent"
            elif seo_score >= 75:
                seo_quality = "Good"
            elif seo_score >= 50:
                seo_quality = "Average"
            elif seo_score >= 25:
                seo_quality = "Below Average"
            else:
                seo_quality = "Poor"
        else:
            meta_description_pct = 0
            meta_keywords_pct = 0
            h1_pct = 0
            h2_pct = 0
            alt_text_pct = 0
            structured_data_pct = 0
            seo_score = 0
            seo_quality = "Unknown"
        
        return {
            "total_pages_analyzed": total_pages,
            "meta_description": {
                "count": pages_with_meta_description,
                "percentage": meta_description_pct
            },
            "meta_keywords": {
                "count": pages_with_meta_keywords,
                "percentage": meta_keywords_pct
            },
            "h1_tags": {
                "count": pages_with_h1,
                "percentage": h1_pct
            },
            "h2_tags": {
                "count": pages_with_h2,
                "percentage": h2_pct
            },
            "alt_text": {
                "count": pages_with_alt_text,
                "percentage": alt_text_pct
            },
            "structured_data": {
                "count": pages_with_structured_data,
                "percentage": structured_data_pct
            },
            "seo_score": seo_score,
            "seo_quality": seo_quality
        }