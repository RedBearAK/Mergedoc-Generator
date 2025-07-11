# Merged Document Generator

A flexible, modular document generation system that creates professional PDFs from data sources with support for repeating sections, complex calculations, and customizable layouts.

## 🚀 Features

- **🔧 Multiple Document Types**: Extensible plugin system (invoices, sales orders, purchase orders, etc.)
- **📊 Smart Data Merging**: Properly groups records and handles repeating line items
- **📄 Professional PDFs**: High-quality output with customizable formatting
- **📁 Multiple Data Sources**: Excel (.xlsx, .xls), CSV, and TSV support
- **🧮 Automatic Calculations**: Built-in totals, subtotals, taxes, and custom calculations
- **⚡ Batch Processing**: Generate individual or merged documents efficiently
- **🐍 Modern Python**: Uses built-in type hints (Python 3.9+)
- **⚙️ External Configuration**: Company information stored in external config files

## 📦 Installation

```bash
# Install dependencies
pip install pandas reportlab PyPDF2 openpyxl

# Clone this repository
git clone https://github.com/yourusername/mergedoc_generator.git
cd mergedoc_generator
```

## 🎯 Quick Start

### 1. First-Time Setup

```bash
# See available document types
python -m mergedoc_generator --list-types

# Set up configuration for invoices (saves to ~/.config/mergedoc_generator/)
python -m mergedoc_generator --type invoice --setup

# OR set up in current directory
python -m mergedoc_generator --type invoice --setup --setup-location local
```

### 2. Customize Your Configuration

Edit the created configuration file to add your company information:

```json
{
  "company": {
    "name": "Your Company Name",           ← Update this
    "address": "Your Address\nCity, State ZIP",  ← Update this  
    "phone": "Your Phone Number",         ← Update this
    "email": "your@email.com"            ← Update this
  }
}
```

### 3. Test with Sample Data

```bash
# Create sample data for testing
python -m mergedoc_generator --type invoice --create-samples

# Generate test documents
python -m mergedoc_generator --type invoice --source sample_invoice_data.xlsx
```

### 4. Use Your Own Data

```bash
# Generate all documents
python -m mergedoc_generator --type invoice --source your_data.xlsx

# Generate specific documents
python -m mergedoc_generator --type invoice --source data.csv --range INV-001 INV-002
```

## Project Structure

```
mergedoc_generator/
├── __init__.py                 # Package initialization
├── __main__.py                 # Entry point for -m execution
├── cli.py                      # Command line interface
├── core/                       # Core framework components
│   ├── __init__.py
│   ├── base.py                 # Base classes and interfaces
│   ├── data_loader.py          # Data loading utilities
│   ├── pdf_builder.py          # PDF generation utilities
│   └── registry.py             # Plugin registry system
└── document_types/             # Document type plugins
    ├── __init__.py
    ├── invoice.py              # Invoice document type
    └── sales_order.py          # Sales order document type
```

## 📋 Data Format Requirements

Your source data should be structured with:

- **Document ID field**: Groups records into documents (e.g., `invoice_number`, `order_number`)  
- **Customer information**: Fields for customer details
- **Line items**: Repeating rows for each document

### Example Data Structure

```csv
invoice_number,customer_name,customer_address,description,quantity,unit_price,invoice_date
INV-001,John Doe,"123 Main St, City, ST 12345",Web Development,40,75.00,2024-01-15
INV-001,John Doe,"123 Main St, City, ST 12345",Domain Registration,1,15.00,2024-01-15
INV-002,Jane Smith,"456 Oak Ave, Other City, ST 67890",Logo Design,1,500.00,2024-01-16
```

## ⚙️ Configuration Management

### Configuration File Locations

The system searches for configuration files in this order:

1. **Specified with `--config`** (highest priority)
2. **Current directory**: `./invoice_config.json`
3. **User config**: `~/.config/mergedoc_generator/invoice_config.json` 
4. **User home**: `~/.mergedoc_generator/invoice_config.json`

```bash
# Check where your configs are located
python -m mergedoc_generator --type invoice --list-configs
```

### Configuration Structure

```json
{
  "document_type": "invoice",
  "company": {
    "name": "Your Company Name",
    "address": "Your Address\nCity, State ZIP",
    "phone": "Your Phone",
    "email": "your@email.com"
  },
  "fields": {
    "document_number_field": "invoice_number",
    "customer_fields": ["customer_name", "customer_address"],
    "line_item_fields": ["description", "quantity", "unit_price"]
  },
  "calculations": {
    "tax_rate": 0.08
  },
  "formatting": {
    "currency_symbol": "$",
    "date_format": "%m/%d/%Y"
  },
  "output": {
    "individual_files": true,
    "output_directory": "invoices"
  }
}
```

## 🔧 Available Document Types

| Document Type | Command | Description |
|---------------|---------|-------------|
| **Invoice** | `--type invoice` | Professional invoices with line items and tax calculations |
| **Sales Order** | `--type sales_order` | Sales orders with shipping info and delivery dates |

More document types can be easily added by following the plugin system.

## 🚀 Usage Examples

```bash
# Basic usage
python -m mergedoc_generator --type invoice --source data.xlsx

# Generate specific documents
python -m mergedoc_generator --type invoice --source data.csv --range INV-001 INV-005

# Use custom configuration
python -m mergedoc_generator --type invoice --source data.xlsx --config my_config.json

# Generate sales orders with verbose output
python -m mergedoc_generator --type sales_order --source orders.xlsx --verbose

# Set up configuration for new document type
python -m mergedoc_generator --type sales_order --setup
```

## 🛠️ Creating New Document Types

The system is designed to be easily extensible. To add a new document type (e.g., purchase orders):

### 1. Create Document Module

Create `mergedoc_generator/document_types/purchase_order.py`:

```python
from mergedoc_generator.core.base import DocumentGenerator, DocumentConfig

def get_document_info():
    return {
        "display_name": "Purchase Order",
        "description": "Purchase orders for procurement"
    }

class DocumentConfig(DocumentConfig):
    def get_default_config(self):
        # Define your document-specific configuration
        pass

class DocumentGenerator(DocumentGenerator):
    def generate_documents(self, data, document_range=None):
        # Implement your document generation logic
        pass

def create_sample_config():
    # Create sample configuration
    pass

def create_sample_data():
    # Create sample data
    pass
```

### 2. Test Your New Document Type

```bash
# The CLI automatically discovers your new type
python -m mergedoc_generator --list-types

# Set up and test
python -m mergedoc_generator --type purchase_order --setup
python -m mergedoc_generator --type purchase_order --source data.xlsx
```

## 📁 Project Structure

```
mergedoc_generator/
├── __init__.py                 # Package initialization
├── __main__.py                 # Entry point for -m execution
├── cli.py                      # Command line interface with auto-discovery
├── core/                       # Core framework components
│   ├── base.py                 # Abstract base classes
│   ├── data_loader.py          # Data loading utilities
│   ├── pdf_builder.py          # PDF generation utilities
│   └── registry.py             # Plugin registry system
└── document_types/             # Document type plugins
    ├── invoice.py              # Invoice documents
    └── sales_order.py          # Sales order documents
```

## 🆚 Advantages Over Traditional Mail Merge

| Feature | Word Mail Merge | Merged Document Generator |
|---------|-----------------|---------------------------|
| **Record Grouping** | ❌ Complex workarounds needed | ✅ Automatic grouping by document ID |
| **Line Item Totals** | ❌ Manual formulas required | ✅ Automatic calculations |
| **Professional Output** | ⚠️ Formatting limitations | ✅ High-quality PDF generation |
| **Data Sources** | ⚠️ Limited compatibility | ✅ Excel, CSV, TSV support |
| **Batch Processing** | ❌ Manual process | ✅ Automated batch generation |
| **Extensibility** | ❌ Hard to customize | ✅ Plugin system for new types |

## 🐛 Troubleshooting

### Common Issues

**"No configuration file found"**
```bash
# Solution: Set up configuration
python -m mergedoc_generator --type invoice --setup
```

**Company shows placeholder text**
```bash
# Solution: Edit your configuration file
python -m mergedoc_generator --type invoice --list-configs
# Then edit the configuration file shown
```

**"Document number field not found"**
- Check that your data contains the field specified in `document_number_field`
- Default field names: `invoice_number` (invoices), `order_number` (sales orders)

**Import/dependency errors**
```bash
# Solution: Install required packages
pip install pandas reportlab PyPDF2 openpyxl
```

### Debug Mode

Enable verbose logging for detailed troubleshooting:

```bash
python -m mergedoc_generator --type invoice --source data.xlsx --verbose
```

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Add new document types** by creating modules in `document_types/`
2. **Improve existing document layouts** and calculations
3. **Add new data source formats** or output options
4. **Improve documentation** and examples
5. **Report bugs** or suggest features

### Development Setup

```bash
git clone https://github.com/yourusername/mergedoc_generator.git
cd mergedoc_generator

# Set up development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install pandas reportlab PyPDF2 openpyxl

# Test the system
python -m mergedoc_generator --list-types
```

## 🙋 Support

- **Documentation**: See this README and the Quick Start Guide
- **Issues**: Report bugs on GitHub Issues
- **Questions**: Use GitHub Discussions

---

**Ready to generate professional documents from your data?** Start with `python -m mergedoc_generator --type invoice --setup` and customize from there!
