# Quick Start Guide

## First-Time Setup

### 1. Install Dependencies
```bash
pip install pandas reportlab PyPDF2 openpyxl
```

### 2. Set Up Your Configuration

**Recommended: User-wide setup** (config saved to `~/.config/mergedoc_generator/`)
```bash
python -m mergedoc_generator --type invoice --setup
```

**Alternative: Project-specific setup** (config saved to current directory)
```bash
python -m mergedoc_generator --type invoice --setup --setup-location local
```

### 3. Customize Your Configuration

The setup command creates a template configuration file. **You must edit this file** to add your company information:

```json
{
  "company": {
    "name": "[YOUR COMPANY NAME]",          ← Replace with your company name
    "address": "[YOUR COMPANY ADDRESS\nCITY, STATE ZIP CODE]",  ← Replace with your address
    "phone": "[YOUR PHONE NUMBER]",        ← Replace with your phone
    "email": "[YOUR EMAIL ADDRESS]"        ← Replace with your email
  }
}
```

### 4. Test with Sample Data

```bash
# Create sample data for testing
python -m mergedoc_generator --type invoice --create-samples

# Generate test invoices
python -m mergedoc_generator --type invoice --source sample_invoice_data.xlsx
```

## Configuration Locations

The system searches for configuration files in this order:

1. **File specified with `--config`** (highest priority)
2. **Current directory**: `./invoice_config.json`
3. **User config directory**: `~/.config/mergedoc_generator/invoice_config.json`
4. **User home directory**: `~/.mergedoc_generator/invoice_config.json`

To see where your configs are located:
```bash
python -m mergedoc_generator --type invoice --list-configs
```

## Available Document Types

```bash
# See all available document types
python -m mergedoc_generator --list-types

# Set up different document types
python -m mergedoc_generator --type sales_order --setup
python -m mergedoc_generator --type purchase_order --setup  # If available
```

## Usage Examples

```bash
# Generate all invoices
python -m mergedoc_generator --type invoice --source invoices.xlsx

# Generate specific invoices
python -m mergedoc_generator --type invoice --source data.csv --range INV-001 INV-002

# Use custom config
python -m mergedoc_generator --type invoice --source data.xlsx --config my_config.json

# Generate sales orders
python -m mergedoc_generator --type sales_order --source orders.xlsx
```

## Data Format

Your data file should have:
- A column to group records by (e.g., `invoice_number`)
- Customer information columns
- Line item columns (description, quantity, price)

Example CSV:
```csv
invoice_number,customer_name,customer_address,description,quantity,unit_price,invoice_date
INV-001,John Doe,"123 Main St, City, ST 12345",Web Development,40,75.00,2024-01-15
INV-001,John Doe,"123 Main St, City, ST 12345",Domain Registration,1,15.00,2024-01-15
```

## Troubleshooting

**"No configuration file found"**
- Run setup: `python -m mergedoc_generator --type invoice --setup`
- Check locations: `python -m mergedoc_generator --type invoice --list-configs`

**Company shows as "[YOUR COMPANY NAME]"**
- Edit your configuration file to replace placeholder values
- Find your config location with `--list-configs`

**"Document number field not found"**
- Check that your data has the field specified in `document_number_field`
- Default is `invoice_number` for invoices, `order_number` for sales orders

## Next Steps

1. ✅ Set up configuration with your company info
2. ✅ Test with sample data
3. ✅ Prepare your real data in the correct format
4. ✅ Generate your documents!

For more details, see the full README.md
