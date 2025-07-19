# mergedoc_generator/document_types/sales_order.py
"""
Sales Order document type for the merged document generator.
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from mergedoc_generator.core.base import (
    DocumentGenerator as BaseDocumentGenerator,
    DocumentConfig as BaseDocumentConfig)
from mergedoc_generator.core.pdf_builder import PDFBuilder
from mergedoc_generator.core.position_converter import (
    Point,
    PositionConverter as pc
)
from reportlab.platypus import Spacer
from reportlab.lib.units import inch

import logging
logger = logging.getLogger(__name__)


def get_document_info() -> dict[str, Any]:
    """Get information about this document type."""
    return {
        "display_name": "Sales Order",
        "description": "Sales orders with line items, shipping info, and delivery dates",
        "version": "1.0.0"
    }


class DocumentConfig(BaseDocumentConfig):
    """Sales Order-specific configuration."""
    
    def get_default_config(self) -> dict[str, Any]:
        """Get default sales order configuration."""
        base_config: dict[str: Any] = super().get_default_config()
        
        sales_order_config = {
            "document_type": "sales_order",
            "company": {
                "name": "[YOUR COMPANY NAME]",
                "address": "[YOUR COMPANY ADDRESS\nCITY, STATE ZIP CODE]",
                "phone": "[YOUR PHONE NUMBER]",
                "email": "[YOUR EMAIL ADDRESS]",
                "website": "[YOUR WEBSITE]"
            },
            "fields": {
                "document_number_field": "order_number",
                "customer_fields": ["customer_name", "customer_address", "customer_email", "customer_phone"],
                "shipping_fields": ["shipping_name", "shipping_address", "shipping_method"],
                "line_item_fields": ["item_code", "description", "quantity", "unit_price"],
                "date_field": "order_date",
                "ship_date_field": "ship_date",
                "delivery_date_field": "delivery_date"
            },
            "calculations": {
                "subtotal_field": "line_total",
                "shipping_cost": 25.00,
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
                "output_directory": "sales_orders",
                "filename_template": "so_{document_number}.pdf"
            }
        }
        
        # Merge with base config
        base_config.update(sales_order_config)
        return base_config


class DocumentGenerator(BaseDocumentGenerator):
    """Sales Order document generator."""
    
    def __init__(self, config: DocumentConfig):
        super().__init__(config)                                # Creates 'self.config'
        self.doc_cfg        = self.config           # Use type hint for config
        self.pdf_builder    = PDFBuilder(self.doc_cfg)
    
    def generate_documents(self, data: pd.DataFrame, document_range: list[str] | None = None) -> list[str]:
        """Generate sales order documents from data."""
        document_field = self.doc_cfg['fields']['document_number_field']
        
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
        if self.doc_cfg['output']['individual_files']:
            for doc_num, doc_data in grouped_data.items():
                filename = self._generate_filename(doc_num)
                filepath = output_dir / filename
                
                self._create_sales_order_pdf(doc_data, str(filepath))
                generated_files.append(str(filepath))
                logger.info(f"Generated sales order: {filepath}")
        
        # Generate merged file if requested
        if self.doc_cfg['output']['merged_file'] and generated_files:
            merged_filename = output_dir / f"merged_sales_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            PDFBuilder.merge_pdfs(generated_files, str(merged_filename))
            logger.info(f"Generated merged file: {merged_filename}")
        
        return generated_files
    
    # def _group_document_data(self, data: pd.DataFrame, document_field: str) -> dict[str, pd.DataFrame]:
    #     """Group data by document number."""
    #     grouped = {}
    #     for doc_num in data[document_field].unique():
    #         doc_data = data[data[document_field] == doc_num].copy()
    #         grouped[str(doc_num)] = doc_data
    #     return grouped

    def _group_document_data(self, data: pd.DataFrame,
                                document_field: str) -> dict[str, pd.DataFrame]:
        """Group data by document number."""
        grouped = {}
        for doc_num in data[document_field].unique():
            # Filter and immediately annotate the result
            filtered_data: pd.DataFrame = data[data[document_field] == doc_num]
            doc_data: pd.DataFrame = filtered_data.copy()
            grouped[str(doc_num)] = doc_data
        return grouped

    def _create_sales_order_pdf(self, order_data: pd.DataFrame, filepath: str) -> None:
        """Create a single sales order PDF."""
        story = []
        
        # Header section
        story.extend(self._create_header(order_data.iloc[0]))
        story.append(Spacer(1, 20))
        
        # Customer and shipping information
        story.extend(self._create_customer_shipping_info(order_data.iloc[0]))
        story.append(Spacer(1, 20))
        
        # Line items table
        story.extend(self._create_line_items_table(order_data))
        story.append(Spacer(1, 20))
        
        # Totals section
        story.extend(self._create_totals_section(order_data))
        story.append(Spacer(1, 20))
        
        # Terms and conditions
        story.extend(self._create_terms_section())
        
        self.pdf_builder.create_document(filepath, story)
    
    def _create_header(self, first_record: pd.Series) -> list[Any]:
        """Create sales order header."""
        company_doc_cfg: dict[str: Any] = self.doc_cfg['company']   # type hint helper
        company_info = f"""
        <b>{self.doc_cfg['company']['name']}</b><br/>
        {self.doc_cfg['company']['address']}<br/>
        Phone: {self.doc_cfg['company']['phone']}<br/>
        Email: {self.doc_cfg['company']['email']}<br/>
        Web: {company_doc_cfg.get('website', '')}
        """
        
        order_num = first_record[self.doc_cfg['fields']['document_number_field']]
        order_date = self.pdf_builder.format_date(
            first_record.get(self.doc_cfg['fields']['date_field'], datetime.now()),
            self.doc_cfg['formatting']['date_format']
        )
        ship_date = self.pdf_builder.format_date(
            first_record.get(self.doc_cfg['fields']['ship_date_field'],
                                datetime.now() + timedelta(days=2)),
            self.doc_cfg['formatting']['date_format']
        )
        delivery_date = self.pdf_builder.format_date(
            first_record.get(self.doc_cfg['fields']['delivery_date_field'],
                                datetime.now() + timedelta(days=7)),
            self.doc_cfg['formatting']['date_format']
        )
        
        order_info = f"""
        <b>SALES ORDER</b><br/>
        Order #: {order_num}<br/>
        Order Date: {order_date}<br/>
        Ship Date: {ship_date}<br/>
        Delivery Date: {delivery_date}
        """
        
        header_table = self.pdf_builder.create_header_table(company_info, order_info)
        return [header_table]
    
    def _create_customer_shipping_info(self, first_record: pd.Series) -> list[Any]:
        """Create customer and shipping information section."""
        from reportlab.platypus import Paragraph
        from reportlab.lib.units import inch
        from reportlab.platypus import Table
        
        # Customer info
        customer_text = "<b>Bill To:</b><br/>"
        for field in self.doc_cfg['fields']['customer_fields']:
            if field in first_record and pd.notna(first_record[field]):
                customer_text += f"{first_record[field]}<br/>"
        
        # Shipping info
        ship_text = "<b>Ship To:</b><br/>"
        for field in self.doc_cfg['fields']['shipping_fields']:
            if field in first_record and pd.notna(first_record[field]):
                ship_text += f"{first_record[field]}<br/>"
        
        info_table = Table([
            [   Paragraph(customer_text, self.pdf_builder.styles['Normal']),
                Paragraph(ship_text, self.pdf_builder.styles['Normal'])]
        ], colWidths=[3*inch, 3*inch])
        
        from reportlab.platypus import TableStyle
        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        return [info_table]
    
    def _create_line_items_table(self, order_data: pd.DataFrame) -> list[Any]:
        """Create line items table."""
        headers = ['Item Code', 'Description', 'Quantity', 'Unit Price', 'Total']
        table_data = [headers]
        
        item_code_field = self.doc_cfg['fields']['line_item_fields'][0]
        desc_field = self.doc_cfg['fields']['line_item_fields'][1]
        qty_field = self.doc_cfg['fields']['line_item_fields'][2]
        price_field = self.doc_cfg['fields']['line_item_fields'][3]
        
        for _, row in order_data.iterrows():
            item_code = str(row.get(item_code_field, ''))
            description = str(row.get(desc_field, ''))
            quantity = float(row.get(qty_field, 0))
            unit_price = float(row.get(price_field, 0))
            line_total = quantity * unit_price
            
            table_data.append([
                item_code,
                description,
                f"{quantity:g}",
                self.pdf_builder.format_currency(
                    unit_price, 
                    self.doc_cfg['formatting']['currency_symbol'],
                    self.doc_cfg['formatting']['number_format']
                ),
                self.pdf_builder.format_currency(
                    line_total,
                    self.doc_cfg['formatting']['currency_symbol'],
                    self.doc_cfg['formatting']['number_format']
                )
            ])
        
        table = self.pdf_builder.create_data_table(
            table_data, 
            col_widths=[1*inch, 2.5*inch, 0.8*inch, 1*inch, 1*inch]
        )
        
        return [table]
    
    def _create_totals_section(self, order_data: pd.DataFrame) -> list[Any]:
        """Create totals section with calculations."""
        qty_field = self.doc_cfg['fields']['line_item_fields'][2]
        price_field = self.doc_cfg['fields']['line_item_fields'][3]
        
        subtotal = 0
        for _, row in order_data.iterrows():
            quantity = float(row.get(qty_field, 0))
            unit_price = float(row.get(price_field, 0))
            subtotal += quantity * unit_price
        
        shipping_cost = self.doc_cfg['calculations']['shipping_cost']
        tax_rate = self.doc_cfg['calculations']['tax_rate']
        tax_amount = subtotal * tax_rate
        total = subtotal + shipping_cost + tax_amount
        
        currency_symbol = self.doc_cfg['formatting']['currency_symbol']
        number_format = self.doc_cfg['formatting']['number_format']
        
        totals_data = [
            ['Subtotal:', self.pdf_builder.format_currency(subtotal, currency_symbol, number_format)],
            ['Shipping:', self.pdf_builder.format_currency(shipping_cost, currency_symbol, number_format)],
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
    
    def _create_terms_section(self) -> list[Any]:
        """Create terms and conditions section."""
        from reportlab.platypus import Paragraph
        
        terms_text = """
        <b>Terms and Conditions:</b><br/>
        • Payment is due within 30 days of delivery<br/>
        • Items remain property of seller until paid in full<br/>
        • Returns accepted within 15 days with prior authorization<br/>
        • Shipping costs are non-refundable<br/>
        • Late payments subject to 1.5% monthly service charge
        """
        
        return [Paragraph(terms_text, self.pdf_builder.styles['Normal'])]


def create_sample_config() -> None:
    """Create a sample configuration file for sales orders."""
    config = DocumentConfig()
    
    sample_config = {
        "document_type": "sales_order",
        "page_size": "letter",
        "margins": {"top": 72, "bottom": 72, "left": 72, "right": 72},
        "company": {
            "name": "ABC Manufacturing",
            "address": "789 Industrial Blvd\nManufacturing City, MC 54321",
            "phone": "(555) 987-6543",
            "email": "orders@abcmfg.com",
            "website": "www.abcmanufacturing.com"
        },
        "fields": {
            "document_number_field": "order_number",
            "customer_fields": ["customer_name", "customer_address", "customer_email", "customer_phone"],
            "shipping_fields": ["shipping_name", "shipping_address", "shipping_method"],
            "line_item_fields": ["item_code", "description", "quantity", "unit_price"],
            "date_field": "order_date",
            "ship_date_field": "ship_date",
            "delivery_date_field": "delivery_date"
        },
        "calculations": {
            "shipping_cost": 25.00,
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
            "output_directory": "generated_sales_orders",
            "filename_template": "so_{document_number}.pdf"
        }
    }
    
    with open('sales_order_config.json', 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print("Sample sales order configuration created: sales_order_config.json")


def create_sample_data() -> None:
    """Create sample data file for testing sales orders."""
    sample_data = {
        'order_number': ['SO-1001', 'SO-1001', 'SO-1001', 'SO-1002', 'SO-1002'],
        'customer_name': ['Tech Solutions Inc', 'Tech Solutions Inc', 'Tech Solutions Inc', 'Global Corp', 'Global Corp'],
        'customer_address': ['456 Tech Park\nSilicon Valley, CA 94000', '456 Tech Park\nSilicon Valley, CA 94000',
                            '456 Tech Park\nSilicon Valley, CA 94000', '789 Corporate Dr\nNew York, NY 10001',
                            '789 Corporate Dr\nNew York, NY 10001'],
        'customer_email': ['orders@techsolutions.com', 'orders@techsolutions.com', 'orders@techsolutions.com',
                            'purchasing@globalcorp.com', 'purchasing@globalcorp.com'],
        'customer_phone': ['(555) 555-0123', '(555) 555-0123', '(555) 555-0123', '(555) 555-0456', '(555) 555-0456'],
        'shipping_name': ['Tech Solutions Inc', 'Tech Solutions Inc', 'Tech Solutions Inc', 'Global Corp Warehouse', 'Global Corp Warehouse'],
        'shipping_address': ['456 Tech Park\nSilicon Valley, CA 94000', '456 Tech Park\nSilicon Valley, CA 94000',
                            '456 Tech Park\nSilicon Valley, CA 94000', '123 Warehouse Rd\nJersey City, NJ 07302',
                            '123 Warehouse Rd\nJersey City, NJ 07302'],
        'shipping_method': ['Ground', 'Ground', 'Ground', 'Express', 'Express'],
        'order_date': ['2024-02-01', '2024-02-01', '2024-02-01', '2024-02-02', '2024-02-02'],
        'ship_date': ['2024-02-03', '2024-02-03', '2024-02-03', '2024-02-03', '2024-02-03'],
        'delivery_date': ['2024-02-08', '2024-02-08', '2024-02-08', '2024-02-05', '2024-02-05'],
        'item_code': ['WDG-001', 'WDG-002', 'ACC-101', 'PRO-500', 'PRO-501'],
        'description': ['Premium Widget Type A', 'Premium Widget Type B', 'Widget Accessory Kit',
                        'Professional Service Package', 'Extended Warranty'],
        'quantity': [25, 15, 5, 1, 1],
        'unit_price': [125.50, 135.75, 45.00, 2500.00, 350.00]
    }
    
    df = pd.DataFrame(sample_data)
    df.to_excel('sample_sales_order_data.xlsx', index=False)
    df.to_csv('sample_sales_order_data.csv', index=False)
    
    print("Sample sales order data files created: sample_sales_order_data.xlsx, sample_sales_order_data.csv")
