# mergedoc_generator/document_types/invoice.py
"""
Invoice document type for the merged document generator.
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from mergedoc_generator.core.base import DocumentGenerator, DocumentConfig
from mergedoc_generator.core.pdf_builder import PDFBuilder
from reportlab.platypus import Spacer
from reportlab.lib.units import inch

import logging
logger = logging.getLogger(__name__)


def get_document_info() -> dict[str, Any]:
    """Get information about this document type."""
    return {
        "display_name": "Invoice",
        "description": "Professional invoices with line items and calculations",
        "version": "1.0.0"
    }


class DocumentConfig(DocumentConfig):
    """Invoice-specific configuration."""
    
    def get_default_config(self) -> dict[str, Any]:
        """Get default invoice configuration."""
        base_config = super().get_default_config()
        
        invoice_config = {
            "document_type": "invoice",
            "company": {
                "name": "[YOUR COMPANY NAME]",
                "address": "[YOUR COMPANY ADDRESS\nCITY, STATE ZIP CODE]",
                "phone": "[YOUR PHONE NUMBER]",
                "email": "[YOUR EMAIL ADDRESS]"
            },
            "fields": {
                "document_number_field": "invoice_number",
                "customer_fields": ["customer_name", "customer_address", "customer_email"],
                "line_item_fields": ["description", "quantity", "unit_price"],
                "date_field": "invoice_date",
                "due_date_field": "due_date"
            },
            "calculations": {
                "subtotal_field": "line_total",
                "tax_rate": 0.08,
                "tax_field": "tax_amount",
                "total_field": "total_amount"
            },
            "formatting": {
                "currency_symbol": "$",
                "date_format": "%m/%d/%Y",
                "number_format": ",.2f"
            },
            "output": {
                "individual_files": True,
                "merged_file": False,
                "output_directory": "invoices",
                "filename_template": "invoice_{document_number}.pdf"
            }
        }
        
        # Merge with base config
        base_config.update(invoice_config)
        return base_config


class DocumentGenerator(DocumentGenerator):
    """Invoice document generator."""
    
    def __init__(self, config: DocumentConfig):
        super().__init__(config)
        self.pdf_builder = PDFBuilder(self.config)
    
    def generate_documents(self, data: pd.DataFrame, document_range: list[str] | None = None) -> list[str]:
        """Generate invoice documents from data."""
        document_field = self.config['fields']['document_number_field']
        
        if document_field not in data.columns:
            raise ValueError(f"Document number field '{document_field}' not found in data")
        
        # Group data by document number
        grouped_data = self._group_document_data(data, document_field)
        
        # Filter by range if specified
        if document_range:
            grouped_data = {k: v for k, v in grouped_data.items() if k in document_range}
        
        generated_files = []
        output_dir = self._create_output_directory()
        
        # Generate individual documents
        if self.config['output']['individual_files']:
            for doc_num, doc_data in grouped_data.items():
                filename = self._generate_filename(doc_num)
                filepath = output_dir / filename
                
                self._create_invoice_pdf(doc_data, str(filepath))
                generated_files.append(str(filepath))
                logger.info(f"Generated invoice: {filepath}")
        
        # Generate merged file if requested
        if self.config['output']['merged_file'] and generated_files:
            merged_filename = output_dir / f"merged_invoices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            PDFBuilder.merge_pdfs(generated_files, str(merged_filename))
            logger.info(f"Generated merged file: {merged_filename}")
        
        return generated_files
    
    def _group_document_data(self, data: pd.DataFrame, document_field: str) -> dict[str, pd.DataFrame]:
        """Group data by document number."""
        grouped = {}
        for doc_num in data[document_field].unique():
            doc_data = data[data[document_field] == doc_num].copy()
            grouped[str(doc_num)] = doc_data
        return grouped
    
    def _create_invoice_pdf(self, invoice_data: pd.DataFrame, filepath: str) -> None:
        """Create a single invoice PDF."""
        story = []
        
        # Header section
        story.extend(self._create_header(invoice_data.iloc[0]))
        story.append(Spacer(1, 20))
        
        # Customer information
        story.extend(self._create_customer_info(invoice_data.iloc[0]))
        story.append(Spacer(1, 20))
        
        # Line items table
        story.extend(self._create_line_items_table(invoice_data))
        story.append(Spacer(1, 20))
        
        # Totals section
        story.extend(self._create_totals_section(invoice_data))
        
        self.pdf_builder.create_document(filepath, story)
    
    def _create_header(self, first_record: pd.Series) -> list[Any]:
        """Create invoice header."""
        company_info = f"""
        <b>{self.config['company']['name']}</b><br/>
        {self.config['company']['address']}<br/>
        Phone: {self.config['company']['phone']}<br/>
        Email: {self.config['company']['email']}
        """
        
        invoice_num = first_record[self.config['fields']['document_number_field']]
        invoice_date = self.pdf_builder.format_date(
            first_record.get(self.config['fields']['date_field'], datetime.now()),
            self.config['formatting']['date_format']
        )
        due_date = self.pdf_builder.format_date(
            first_record.get(self.config['fields']['due_date_field'], datetime.now()),
            self.config['formatting']['date_format']
        )
        
        invoice_info = f"""
        <b>INVOICE</b><br/>
        Invoice #: {invoice_num}<br/>
        Date: {invoice_date}<br/>
        Due Date: {due_date}
        """
        
        header_table = self.pdf_builder.create_header_table(company_info, invoice_info)
        return [header_table]
    
    def _create_customer_info(self, first_record: pd.Series) -> list[Any]:
        """Create customer information section."""
        from reportlab.platypus import Paragraph
        
        bill_to_text = "<b>Bill To:</b><br/>"
        for field in self.config['fields']['customer_fields']:
            if field in first_record and pd.notna(first_record[field]):
                bill_to_text += f"{first_record[field]}<br/>"
        
        return [Paragraph(bill_to_text, self.pdf_builder.styles['Normal'])]
    
    def _create_line_items_table(self, invoice_data: pd.DataFrame) -> list[Any]:
        """Create line items table."""
        headers = ['Description', 'Quantity', 'Unit Price', 'Total']
        table_data = [headers]
        
        desc_field = self.config['fields']['line_item_fields'][0]
        qty_field = self.config['fields']['line_item_fields'][1]
        price_field = self.config['fields']['line_item_fields'][2]
        
        for _, row in invoice_data.iterrows():
            description = str(row.get(desc_field, ''))
            quantity = float(row.get(qty_field, 0))
            unit_price = float(row.get(price_field, 0))
            line_total = quantity * unit_price
            
            table_data.append([
                description,
                f"{quantity:g}",
                self.pdf_builder.format_currency(
                    unit_price, 
                    self.config['formatting']['currency_symbol'],
                    self.config['formatting']['number_format']
                ),
                self.pdf_builder.format_currency(
                    line_total,
                    self.config['formatting']['currency_symbol'],
                    self.config['formatting']['number_format']
                )
            ])
        
        table = self.pdf_builder.create_data_table(
            table_data, 
            col_widths=[3*inch, 1*inch, 1*inch, 1*inch]
        )
        
        return [table]
    
    def _create_totals_section(self, invoice_data: pd.DataFrame) -> list[Any]:
        """Create totals section with calculations."""
        qty_field = self.config['fields']['line_item_fields'][1]
        price_field = self.config['fields']['line_item_fields'][2]
        
        subtotal = 0
        for _, row in invoice_data.iterrows():
            quantity = float(row.get(qty_field, 0))
            unit_price = float(row.get(price_field, 0))
            subtotal += quantity * unit_price
        
        tax_rate = self.config['calculations']['tax_rate']
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount
        
        currency_symbol = self.config['formatting']['currency_symbol']
        number_format = self.config['formatting']['number_format']
        
        totals_data = [
            ['Subtotal:', self.pdf_builder.format_currency(subtotal, currency_symbol, number_format)],
            [f'Tax ({tax_rate*100:.1f}%):', self.pdf_builder.format_currency(tax_amount, currency_symbol, number_format)],
            ['Total:', self.pdf_builder.format_currency(total, currency_symbol, number_format)]
        ]
        
        from reportlab.lib import colors
        from reportlab.platypus import TableStyle
        
        totals_table = self.pdf_builder.create_data_table(
            totals_data,
            col_widths=[4*inch, 1.5*inch],
            has_header=False
        )
        
        # Add special styling for totals
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0, colors.white),  # Remove grid
        ]))
        
        return [totals_table]


def create_sample_config() -> None:
    """Create a sample configuration file for invoices."""
    sample_config = {
        "document_type": "invoice",
        "page_size": "letter",
        "margins": {"top": 72, "bottom": 72, "left": 72, "right": 72},
        "company": {
            "name": "Acme Corporation",
            "address": "123 Business Ave\nSuite 100\nBusiness City, BC 12345",
            "phone": "(555) 123-4567",
            "email": "billing@acme.com"
        },
        "fields": {
            "document_number_field": "invoice_number",
            "customer_fields": ["customer_name", "customer_address", "customer_email"],
            "line_item_fields": ["description", "quantity", "unit_price"],
            "date_field": "invoice_date",
            "due_date_field": "due_date"
        },
        "calculations": {
            "tax_rate": 0.08
        },
        "formatting": {
            "currency_symbol": "$",
            "date_format": "%m/%d/%Y",
            "number_format": ",.2f"
        },
        "output": {
            "individual_files": True,
            "merged_file": False,
            "output_directory": "generated_invoices",
            "filename_template": "invoice_{document_number}.pdf"
        }
    }
    
    with open('invoice_config.json', 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print("Sample invoice configuration created: invoice_config.json")
    print("⚠️  This contains example company information - please customize!")
    print("💡 For permanent setup, use: python -m mergedoc_generator --type invoice --setup")


def create_sample_data() -> None:
    """Create sample data file for testing invoices."""
    sample_data = {
        'invoice_number': ['INV-001', 'INV-001', 'INV-001', 'INV-002', 'INV-002'],
        'customer_name': ['John Doe', 'John Doe', 'John Doe', 'Jane Smith', 'Jane Smith'],
        'customer_address': ['123 Main St\nAnytown, ST 12345', '123 Main St\nAnytown, ST 12345', 
                           '123 Main St\nAnytown, ST 12345', '456 Oak Ave\nOther City, ST 67890',
                           '456 Oak Ave\nOther City, ST 67890'],
        'customer_email': ['john@example.com', 'john@example.com', 'john@example.com',
                          'jane@example.com', 'jane@example.com'],
        'invoice_date': ['2024-01-15', '2024-01-15', '2024-01-15', '2024-01-16', '2024-01-16'],
        'due_date': ['2024-02-15', '2024-02-15', '2024-02-15', '2024-02-16', '2024-02-16'],
        'description': ['Web Development Services', 'Domain Registration', 'SSL Certificate',
                       'Logo Design', 'Business Cards'],
        'quantity': [40, 1, 1, 1, 500],
        'unit_price': [75.00, 15.00, 50.00, 500.00, 0.50]
    }
    
    df = pd.DataFrame(sample_data)
    df.to_excel('sample_invoice_data.xlsx', index=False)
    df.to_csv('sample_invoice_data.csv', index=False)
    
    print("Sample invoice data files created: sample_invoice_data.xlsx, sample_invoice_data.csv")
