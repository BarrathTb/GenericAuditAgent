# main.py - Entry point for the Generic AI Audit Agent
# This script provides a web interface for the audit agent using Flask

import os
import sys
import json
import subprocess
import threading
import queue
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import components
from extractor.extractor import ProductExtractor
from analyzer.analyzer import ProductAnalyzer
from reporter.reporter import ProductReporter

# Initialize Flask app
app = Flask(__name__, 
            static_folder='ui/static',
            template_folder='ui/templates')

# Global variables to track audit state
audit_status = {
    "running": False,
    "step": "not_started",
    "progress": 0,
    "log": [],
    "stop_requested": False
}

# Queue for log messages
log_queue = queue.Queue()

def setup_directories():
    """Ensure all necessary data directories exist."""
    directories = [
        "data/raw",
        "data/processed",
        "data/analyzed",
        "data/reports"
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def add_log_message(message):
    """Add a message to the log queue."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_queue.put(f"[{timestamp}] {message}")
    
    # Update the global log
    while not log_queue.empty():
        audit_status["log"].append(log_queue.get())
        # Keep log at a reasonable size
        if len(audit_status["log"]) > 100:
            audit_status["log"].pop(0)

def run_crawler(config):
    """Run the Scrapy crawler with the specified parameters."""
    global audit_status
    
    try:
        # Update status
        audit_status["running"] = True
        audit_status["step"] = "crawling"
        audit_status["progress"] = 10
        
        # Extract configuration
        start_url = config["start_url"]
        allowed_domain = config["allowed_domain"]
        
        # Log start
        add_log_message(f"Starting crawler at {start_url} (domain: {allowed_domain})")
        
        # Generate output filename
        domain_name = allowed_domain.replace(".", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join("data", "raw", f"{domain_name}_{timestamp}.json")
        
        # Get the current directory and ensure we're in the correct directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        crawler_dir = os.path.join(current_dir, "crawler")
        
        # Make sure the crawler directory exists
        if not os.path.exists(crawler_dir):
            add_log_message(f"Crawler directory not found at: {crawler_dir}")
            audit_status["running"] = False
            audit_status["step"] = "failed"
            return False, None
            
        # Adjust the output file path to be relative to the crawler directory
        abs_output_file = os.path.abspath(os.path.join(current_dir, output_file))
        rel_output_file = os.path.relpath(abs_output_file, crawler_dir)
        
        # Build the command
        command = [
            "scrapy", "crawl", "generic_spider",
            "-a", f"start_urls={start_url}",
            "-a", f"allowed_domains={allowed_domain}",
            "-o", rel_output_file
        ]
        
        # Add product URL patterns if provided
        if config.get("product_url_patterns"):
            patterns_json = json.dumps(config["product_url_patterns"])
            command.extend(["-a", f"product_url_patterns={patterns_json}"])
        
        # Add product page selectors if provided
        if config.get("product_page_selectors"):
            selectors_json = json.dumps(config["product_page_selectors"])
            command.extend(["-a", f"product_page_selectors={selectors_json}"])
        
        # Process extract fields and add appropriate selectors
        extract_fields = config.get("extract_fields", [])
        
        # Default selectors for common fields
        default_selectors = {
            "name": ["h1.product-title::text", "h1[itemprop='name']::text", "h1::text", ".page-title span::text"],
            "price": [".price::text", "[itemprop='price']::text", ".product-price::text", "span.price::text", ".product-info-price .price::text"],
            "description": [".product-description", "[itemprop='description']", ".description", ".product.attribute.description .value", "div.product.attribute.description"],
            "sku": ["[itemprop='sku']::text", ".product-sku::text", ".sku::text", ".product.attribute.sku .value::text"],
            "images": [".product-image::attr(src)", "[itemprop='image']::attr(src)", ".product img::attr(src)", ".gallery-placeholder img::attr(src)", ".fotorama__img::attr(src)"],
            "specs": [".product-specs", ".specifications", "table.specs", ".additional-attributes", ".product-attributes"]
        }
        
        # Add selectors based on selected fields
        for field in extract_fields:
            if field in default_selectors:
                # If user provided custom selectors, use those
                selector_key = f"product_{field}_selectors"
                if config.get(selector_key):
                    selectors_json = json.dumps(config[selector_key])
                else:
                    # Otherwise use default selectors
                    selectors_json = json.dumps(default_selectors[field])
                
                command.extend(["-a", f"product_{field}_selectors={selectors_json}"])
        
        # Add custom fields if provided
        if config.get("custom_fields"):
            fields_json = json.dumps(config["custom_fields"])
            command.extend(["-a", f"custom_fields={fields_json}"])
            
        # Log the selected fields
        add_log_message(f"Selected fields to extract: {', '.join(extract_fields)}")
        
        # Log the command
        add_log_message(f"Running command: {' '.join(command)}")
        
        # Log the crawler directory
        add_log_message(f"Using crawler directory: {crawler_dir}")
        
        # Change to the crawler directory
        os.chdir(crawler_dir)
        
        # Add crawl limit if specified
        if config.get("crawl_limit"):
            command.extend(["-a", f"crawl_limit={config['crawl_limit']}"])
            add_log_message(f"Setting crawl limit to {config['crawl_limit']} pages")
        
        # Add delay to avoid Cloudflare protection
        command.extend(["-s", "DOWNLOAD_DELAY=2"])
        
        # Add user agent to avoid being blocked
        command.extend(["-s", "USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"])
        
        # Run the crawler
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Process output in real-time
        for line in process.stdout:
            add_log_message(line.strip())
            
            # Check if stop was requested
            if audit_status["stop_requested"]:
                add_log_message("Stop requested. Terminating crawler...")
                process.terminate()
                break
        
        # Wait for process to complete
        process.wait()
        
        # Change back to the current directory
        os.chdir(current_dir)
        
        # Check if the process was successful or if it was stopped by user request
        if process.returncode == 0 or audit_status["stop_requested"]:
            if process.returncode == 0:
                add_log_message(f"Crawler completed successfully. Output saved to {output_file}")
            else:
                add_log_message(f"Crawler stopped by user request. Partial data saved to {output_file}")
            
            audit_status["progress"] = 30
            
            # Process the data
            process_data(output_file, config.get("report_formats", ["text", "html", "csv"]))
            
            return True, output_file
        else:
            add_log_message(f"Crawler failed with return code {process.returncode}")
            audit_status["running"] = False
            audit_status["step"] = "failed"
            return False, None
            
    except Exception as e:
        add_log_message(f"Error running crawler: {str(e)}")
        audit_status["running"] = False
        audit_status["step"] = "failed"
        return False, None

def process_data(raw_data_file, report_formats):
    """Process the raw data, analyze it, and generate reports."""
    global audit_status
    
    try:
        # Extract data
        audit_status["step"] = "extracting"
        audit_status["progress"] = 40
        add_log_message("Starting data extraction...")
        
        extractor = ProductExtractor()
        processed_file = extractor.process_file(os.path.basename(raw_data_file))
        
        add_log_message(f"Data extraction completed. Output saved to {processed_file}")
        audit_status["progress"] = 60
        
        # Analyze data
        audit_status["step"] = "analyzing"
        add_log_message("Starting data analysis...")
        
        analyzer = ProductAnalyzer()
        analysis_file = analyzer.analyze_file(os.path.basename(processed_file))
        
        add_log_message(f"Data analysis completed. Output saved to {analysis_file}")
        audit_status["progress"] = 80
        
        # Generate reports
        audit_status["step"] = "reporting"
        add_log_message("Generating reports...")
        
        reporter = ProductReporter()
        report_files = reporter.generate_report(os.path.basename(analysis_file), formats=report_formats)
        
        add_log_message("Report generation completed.")
        for format_type, file_path in report_files.items():
            add_log_message(f"{format_type.upper()} report saved to {file_path}")
        
        # Complete the audit
        audit_status["progress"] = 100
        audit_status["step"] = "completed"
        audit_status["running"] = False
        
        add_log_message("Audit completed successfully.")
        
        return True
    except Exception as e:
        add_log_message(f"Error processing data: {str(e)}")
        audit_status["running"] = False
        audit_status["step"] = "failed"
        return False

def run_audit_in_thread(config):
    """Run the audit process in a separate thread."""
    thread = threading.Thread(target=run_crawler, args=(config,))
    thread.daemon = True
    thread.start()

# Flask routes
@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/start_audit', methods=['POST'])
def start_audit():
    """Start the audit process."""
    global audit_status
    
    # Check if an audit is already running
    if audit_status["running"]:
        return jsonify({"status": "error", "message": "An audit is already running"})
    
    # Get configuration from request
    config = request.json
    
    # Reset audit status
    audit_status = {
        "running": True,
        "step": "starting",
        "progress": 0,
        "log": [],
        "stop_requested": False
    }
    
    # Start the audit in a separate thread
    run_audit_in_thread(config)
    
    return jsonify({"status": "success", "message": "Audit started"})

@app.route('/audit_status')
def get_audit_status():
    """Get the current status of the audit."""
    return jsonify(audit_status)

@app.route('/clear_log')
def clear_log():
    """Clear the audit log."""
    global audit_status
    audit_status["log"] = []
    return jsonify({"status": "success"})

@app.route('/stop_audit', methods=['POST'])
def stop_audit():
    """Stop the running audit and generate reports with collected data."""
    global audit_status
    
    if not audit_status["running"]:
        return jsonify({"status": "error", "message": "No audit is currently running"})
    
    # Set the stop flag
    audit_status["stop_requested"] = True
    add_log_message("User requested to stop the audit")
    
    # The actual processing will happen in the run_crawler function
    # when it detects the stop_requested flag
    
    return jsonify({"status": "success", "message": "Stop request received"})

@app.route('/reports')
def get_reports():
    """Get a list of available reports."""
    reports_dir = os.path.join("data", "reports")
    
    if not os.path.exists(reports_dir):
        return jsonify({"text": [], "html": [], "csv": []})
    
    reports = {
        'text': [],
        'html': [],
        'csv': []
    }
    
    for filename in os.listdir(reports_dir):
        if filename.endswith('.txt'):
            reports['text'].append(filename)
        elif filename.endswith('.html'):
            reports['html'].append(filename)
        elif filename.endswith('.csv'):
            reports['csv'].append(filename)
    
    return jsonify(reports)

@app.route('/report/<path:filename>')
def get_report(filename):
    """Get a specific report file."""
    return send_from_directory(os.path.join("data", "reports"), filename)

def main():
    """Main entry point for the Generic AI Audit Agent."""
    # Set up directories
    setup_directories()
    
    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()