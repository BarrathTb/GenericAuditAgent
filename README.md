# Generic AI Audit Agent

A configurable web crawler and content analyzer for auditing websites, extracting product information, and generating comprehensive reports.

## Features

- **Web Crawling**: Configurable crawler that can be tailored to any website structure
- **Product Detection**: Intelligent product page identification using URL patterns and page elements
- **Data Extraction**: Extract product details, specifications, and related content
- **Content Analysis**: Analyze content quality, readability, and SEO metrics
- **Reporting**: Generate reports in multiple formats (Text, HTML, CSV)
- **Web UI**: User-friendly interface for configuration and monitoring
- **Customizable**: Add custom fields and selectors for specific website structures

## Project Structure

```
GenericAuditAgent/
├── crawler/                 # Scrapy crawler component
│   ├── audit_crawler/       # Scrapy project
│   │   ├── spiders/         # Spider definitions
│   │   │   ├── generic_spider.py  # Main spider for crawling
│   │   ├── settings.py      # Scrapy settings
│   ├── scrapy.cfg           # Scrapy configuration
├── extractor/               # Data extraction component
├── analyzer/                # Data analysis component
├── reporter/                # Report generation component
├── data/                    # Data storage
│   ├── raw/                 # Raw crawler output
│   ├── processed/           # Processed data
│   ├── analyzed/            # Analysis results
│   ├── reports/             # Generated reports
├── ui/                      # Web UI
│   ├── templates/           # HTML templates
│   ├── static/              # Static assets (CSS, JS)
├── main.py                  # Main application entry point
├── requirements.txt         # Project dependencies
```

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/GenericAuditAgent.git
   cd GenericAuditAgent
   ```

2. Create a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Download required NLTK data:

   ```python
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

5. Download required spaCy model:
   ```
   python -m spacy download en_core_web_sm
   ```

## Usage

### Starting the Web UI

Run the following command to start the web UI:

```
python main.py
```

By default, the UI will be available at http://localhost:5000

### Configuration Options

The web UI provides the following configuration options:

#### Basic Configuration

- **Starting URL**: The URL where the crawler will begin
- **Allowed Domain**: The domain(s) the crawler is allowed to visit

#### Product Identification

- **Product URL Patterns**: Regular expressions to identify product URLs
- **Product Page Selectors**: CSS selectors to identify product pages

#### Data Extraction

- **Product Name Selectors**: CSS selectors to extract product names
- **Product Price Selectors**: CSS selectors to extract product prices
- **Product Description Selectors**: CSS selectors to extract product descriptions
- **Product SKU Selectors**: CSS selectors to extract product SKUs
- **Product Image Selectors**: CSS selectors to extract product images

#### Custom Fields

- Add custom fields with corresponding CSS selectors to extract additional data

#### Report Configuration

- Select which report formats to generate (Text, HTML, CSV)

### Command Line Usage

You can also run the agent from the command line:

```
python main.py --port 5000 --debug
```

Options:

- `--port`: Port to run the web UI on (default: 5000)
- `--debug`: Run in debug mode

## Customizing the Agent

### Adding Custom Selectors

The Generic AI Audit Agent is designed to be highly customizable. You can add custom selectors for different websites by:

1. Using the web UI to configure selectors for specific websites
2. Modifying the `generic_spider.py` file to add new default selectors

### Extending Functionality

To extend the agent's functionality:

1. Add new analysis methods in the `analyzer` component
2. Create new report templates in the `reporter` component
3. Enhance the web UI by modifying the templates and static files

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Scrapy](https://scrapy.org/) for the powerful web crawling framework
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [NLTK](https://www.nltk.org/) and [spaCy](https://spacy.io/) for natural language processing
- [Pandas](https://pandas.pydata.org/) for data processing
