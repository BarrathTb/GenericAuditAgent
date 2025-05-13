# Reporter Component

The Reporter component is responsible for generating reports from the analysis results produced by the Analyzer component.

## Structure

```
reporter/
├── reporter.py    # Main reporter implementation
├── templates/     # HTML report templates
│   └── report_template.html  # Default HTML template
└── README.md     # This documentation file
```

## ProductReporter Class

The `reporter.py` file contains the `ProductReporter` class, which is responsible for:

1. Loading analysis results from the Analyzer component
2. Generating reports in various formats (text, HTML, CSV)
3. Creating visualizations and charts for the reports
4. Providing recommendations based on the analysis results

### Key Features

- **Multi-format Reporting**: Generate reports in text, HTML, and CSV formats
- **Data Visualization**: Create charts and graphs to visualize analysis results
- **Recommendation Generation**: Provide actionable recommendations based on analysis
- **Customizable Templates**: Use Jinja2 templates for HTML report generation
- **Executive Summary**: Provide a high-level overview of the analysis results

### Usage

The reporter can be used as follows:

```python
from reporter.reporter import ProductReporter

# Initialize the reporter
reporter = ProductReporter(
    input_dir="data/analyzed",
    output_dir="data/reports"
)

# Generate reports
output_files = reporter.generate_report(
    "analyzed_data.json",
    formats=["text", "html", "csv"]
)

print("Reports generated:")
for format_type, file_path in output_files.items():
    print(f"- {format_type.upper()}: {file_path}")
```

## Report Formats

The reporter generates reports in the following formats:

### Text Reports

Text reports (`.txt`) provide a simple, readable format that can be viewed in any text editor. They include:

- Executive summary
- Product analyses
- SEO analysis
- Content quality analysis
- Recommendations

### HTML Reports

HTML reports (`.html`) provide a rich, interactive format that can be viewed in a web browser. They include:

- Styled presentation of all analysis results
- Interactive charts and visualizations
- Collapsible sections for detailed information
- Formatted recommendations
- Visual indicators for scores and metrics

### CSV Reports

CSV reports (`.csv`) provide a tabular format that can be imported into spreadsheet applications or databases. They include:

- One row per product
- Columns for all analyzed metrics
- Suitable for further data analysis or integration with other systems

## Customization

The reporter component can be customized by:

1. Modifying the report generation methods to change the report format and content
2. Creating custom HTML templates in the `templates` directory
3. Adding new visualization types for the HTML reports
4. Extending the recommendation generation logic
5. Adding support for additional report formats (e.g., PDF, JSON)

## Integration

The Reporter component is designed to work seamlessly with the other components of the Generic AI Audit Agent:

- It takes input from the **Analyzer** component
- It produces the final output of the analysis pipeline
- It is orchestrated by the main application

## Future Enhancements

Potential enhancements for the Reporter component include:

- PDF report generation
- Interactive web dashboard for exploring results
- Email delivery of reports
- Scheduled report generation
- Comparison reports between different analyses
- Custom branding and styling options
