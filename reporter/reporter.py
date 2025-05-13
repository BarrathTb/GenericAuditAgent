# reporter.py - Generate reports from analysis results

import os
import json
from datetime import datetime
import csv

class ProductReporter:
    """
    Generate reports from analysis results.
    This component takes the analysis results and generates reports in various formats.
    """
    
    def __init__(self, input_dir="data/analyzed", output_dir="data/reports"):
        """
        Initialize the ProductReporter.
        
        Args:
            input_dir (str): Directory containing analysis result files
            output_dir (str): Directory to save generated reports
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_report(self, filename, formats=None):
        """
        Generate reports from an analysis result file.
        
        Args:
            filename (str): Name of the analysis result file
            formats (list): List of report formats to generate (text, html, csv)
            
        Returns:
            dict: Paths to the generated report files
        """
        if formats is None:
            formats = ['text', 'html', 'csv']
        
        # Construct full input path
        input_path = os.path.join(self.input_dir, filename)
        
        # Generate base output filename
        base_output_name = os.path.splitext(filename)[0].replace('analyzed_', '')
        
        print(f"Generating reports for {input_path}")
        
        # Load analysis results
        with open(input_path, 'r', encoding='utf-8') as f:
            analysis_results = json.load(f)
        
        # Generate reports in requested formats
        output_files = {}
        
        if 'text' in formats:
            text_output_path = os.path.join(self.output_dir, f"{base_output_name}.txt")
            self._generate_text_report(analysis_results, text_output_path)
            output_files['text'] = text_output_path
        
        if 'html' in formats:
            html_output_path = os.path.join(self.output_dir, f"{base_output_name}.html")
            self._generate_html_report(analysis_results, html_output_path)
            output_files['html'] = html_output_path
        
        if 'csv' in formats:
            csv_output_path = os.path.join(self.output_dir, f"{base_output_name}.csv")
            self._generate_csv_report(analysis_results, csv_output_path)
            output_files['csv'] = csv_output_path
        
        return output_files
    
    def _generate_text_report(self, analysis_results, output_path):
        """
        Generate a text report from analysis results.
        
        Args:
            analysis_results (dict): Analysis results
            output_path (str): Path to save the text report
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write report header
            f.write("=" * 80 + "\n")
            f.write("WEBSITE AUDIT REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            # Write report metadata
            f.write("REPORT INFORMATION\n")
            f.write("-" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Analysis Date: {analysis_results['metadata']['analysis_timestamp']}\n")
            f.write(f"Products Analyzed: {analysis_results['metadata']['product_count']}\n")
            f.write(f"Articles Analyzed: {analysis_results['metadata']['article_count']}\n\n")
            
            # Write executive summary
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 80 + "\n")
            f.write("This is a basic report template. The full implementation will include detailed analysis.\n\n")
            
            # Write footer
            f.write("=" * 80 + "\n")
            f.write("End of Report\n")
            f.write("=" * 80 + "\n")
    
    def _generate_html_report(self, analysis_results, output_path):
        """
        Generate an HTML report from analysis results.
        
        Args:
            analysis_results (dict): Analysis results
            output_path (str): Path to save the HTML report
        """
        # Basic HTML template
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Audit Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }}
        h1 {{ color: #2c3e50; text-align: center; }}
        .section {{ margin-bottom: 20px; padding: 15px; background-color: #f9f9f9; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>Website Audit Report</h1>
    
    <div class="section">
        <h2>Report Information</h2>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Analysis Date: {analysis_results['metadata']['analysis_timestamp']}</p>
        <p>Products Analyzed: {analysis_results['metadata']['product_count']}</p>
        <p>Articles Analyzed: {analysis_results['metadata']['article_count']}</p>
    </div>
    
    <div class="section">
        <h2>Executive Summary</h2>
        <p>This is a basic report template. The full implementation will include detailed analysis.</p>
    </div>
    
    <footer>
        <p>&copy; 2025 Generic AI Audit Agent</p>
    </footer>
</body>
</html>"""
        
        # Write the HTML report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_csv_report(self, analysis_results, output_path):
        """
        Generate a CSV report from analysis results.
        
        Args:
            analysis_results (dict): Analysis results
            output_path (str): Path to save the CSV report
        """
        # Extract product data for CSV
        products_data = []
        
        for product in analysis_results.get('product_analyses', []):
            product_data = {
                'Product Name': product.get('product_name', 'Unknown'),
                'Product ID/SKU': product.get('product_id', 'N/A'),
                'URL': product.get('url', 'N/A')
            }
            
            # Add basic analysis data if available
            if 'description_analysis' in product:
                desc = product['description_analysis']
                product_data['Word Count'] = desc.get('word_count', 'N/A')
            
            products_data.append(product_data)
        
        # Write CSV file
        if products_data:
            # Get all unique keys
            fieldnames = set()
            for product in products_data:
                fieldnames.update(product.keys())
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
                writer.writeheader()
                writer.writerows(products_data)
        else:
            # Create an empty CSV with basic headers
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Product Name', 'Product ID/SKU', 'URL', 'Word Count'])
    
    def _generate_recommendations(self, analysis_results):
        """
        Generate recommendations based on analysis results.
        
        Args:
            analysis_results (dict): Analysis results
            
        Returns:
            dict: Recommendations by category
        """
        # Basic recommendations
        return {
            'SEO': [
                "Ensure all pages have meta descriptions",
                "Add alt text to all images"
            ],
            'Content': [
                "Improve product descriptions",
                "Enhance readability of content"
            ],
            'Technical': [
                "Optimize page load speed",
                "Ensure mobile-friendly design"
            ]
        }