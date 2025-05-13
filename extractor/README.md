# Extractor Component

The Extractor component is responsible for processing the raw data collected by the Crawler component and extracting structured information for analysis.

## Structure

```
extractor/
├── extractor.py    # Main extractor implementation
└── README.md      # This documentation file
```

## ProductExtractor Class

The `extractor.py` file contains the `ProductExtractor` class, which is responsible for:

1. Loading raw crawler output (JSON files)
2. Processing and cleaning the data
3. Extracting structured information
4. Saving the processed data for further analysis

### Key Features

- **Text Cleaning**: Removes HTML tags, extra whitespace, and normalizes text
- **Price Extraction**: Extracts numeric price values from price text
- **Dimension Extraction**: Parses product dimensions from specifications
- **Data Structuring**: Organizes data into a consistent format for analysis

### Usage

The extractor can be used as follows:

```python
from extractor.extractor import ProductExtractor

# Initialize the extractor
extractor = ProductExtractor(
    input_dir="data/raw",
    output_dir="data/processed"
)

# Process a file
output_file = extractor.process_file("raw_data.json")

print(f"Processed data saved to: {output_file}")
```

## Customization

The extractor component can be customized by:

1. Modifying the `_process_data` method to change how data is processed
2. Adding new extraction methods for specific types of data
3. Extending the `ProductExtractor` class to support different data formats

## Integration

The Extractor component is designed to work seamlessly with the other components of the Generic AI Audit Agent:

- It takes input from the **Crawler** component
- It provides output to the **Analyzer** component
- It is orchestrated by the main application

## Future Enhancements

Potential enhancements for the Extractor component include:

- Support for additional input formats (CSV, XML, etc.)
- Advanced text processing using NLP techniques
- Image data extraction and processing
- Parallel processing for large datasets
