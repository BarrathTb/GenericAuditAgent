# process_file.py - Process a specific raw data file through the entire pipeline

import os
import sys
import shutil
import nltk
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Download required NLTK resources
print("Downloading required NLTK resources...")
nltk.download('punkt')
nltk.download('stopwords')

# Try to download punkt_tab specifically
try:
    print("Attempting to download punkt_tab...")
    nltk.download('punkt_tab')
except Exception as e:
    print(f"Warning: Could not download punkt_tab: {str(e)}")
    print("Will attempt to continue with available resources.")

# Import components
from extractor.extractor import ProductExtractor
from analyzer.analyzer import ProductAnalyzer
from reporter.reporter import ProductReporter

def process_file(raw_data_file, report_formats=None):
    """Process the raw data, analyze it, and generate reports."""
    
    if report_formats is None:
        report_formats = ["text", "html", "csv"]
    
    try:
        print(f"Starting processing of file: {raw_data_file}")
        
        # Get the basename of the file
        basename = os.path.basename(raw_data_file)
        
        # Check if we need to copy the file to the data/raw directory
        target_path = os.path.join("data", "raw", basename)
        if not os.path.exists(target_path) and os.path.exists(raw_data_file):
            # Ensure the target directory exists
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            # Copy the file
            print(f"Copying file from {raw_data_file} to {target_path}")
            shutil.copy2(raw_data_file, target_path)
        
        # Extract data
        print("Starting data extraction...")
        extractor = ProductExtractor()
        processed_file = extractor.process_file(basename)
        print(f"Data extraction completed. Output saved to {processed_file}")
        
        # Analyze data
        print("Starting data analysis...")
        analyzer = ProductAnalyzer()
        analysis_file = analyzer.analyze_file(os.path.basename(processed_file))
        print(f"Data analysis completed. Output saved to {analysis_file}")
        
        # Generate reports
        print("Generating reports...")
        reporter = ProductReporter()
        report_files = reporter.generate_report(os.path.basename(analysis_file), formats=report_formats)
        
        print("Report generation completed.")
        for format_type, file_path in report_files.items():
            print(f"{format_type.upper()} report saved to {file_path}")
        
        print("Processing completed successfully.")
        return True
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        return False

if __name__ == "__main__":
    # Check if a file path was provided
    if len(sys.argv) > 1:
        raw_data_file = sys.argv[1]
    else:
        # Use the specified file with the correct path
        raw_data_file = "GenericAuditAgent/data/raw/www_petersenproducts_com_20250512_230136.json"
    
    # Process the file
    process_file(raw_data_file)