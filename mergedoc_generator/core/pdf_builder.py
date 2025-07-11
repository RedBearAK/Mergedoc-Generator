# mergedoc_generator/core/pdf_builder.py
"""
PDF building utilities using ReportLab.
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Any
import logging

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from PyPDF2 import PdfWriter, PdfReader

logger = logging.getLogger(__name__)


class PDFBuilder:
    """Utility class for building PDFs with common layouts."""
    
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self) -> None:
        """Set up custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='DocumentTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.black,
            alignment=TA_RIGHT
        ))
        
        self.styles.add(ParagraphStyle(
            name='CompanyInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=0
        ))
    
    def create_document(self, filepath: str, story: list[Any]) -> None:
        """Create a PDF document with the given story elements."""
        page_size = A4 if self.config.get('page_size') == 'A4' else letter
        margins = self.config.get('margins', {})
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=page_size,
            topMargin=margins.get('top', 72),
            bottomMargin=margins.get('bottom', 72),
            leftMargin=margins.get('left', 72),
            rightMargin=margins.get('right', 72)
        )
        
        doc.build(story)
    
    def create_header_table(self, left_content: str, right_content: str, 
                          left_width: float = 3*inch, right_width: float = 3*inch) -> Table:
        """Create a two-column header table."""
        header_table = Table([
            [Paragraph(left_content, self.styles['Normal']), 
             Paragraph(right_content, self.styles['Normal'])]
        ], colWidths=[left_width, right_width])
        
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        
        return header_table
    
    def create_data_table(self, data: list[list[str]], col_widths: list[float] | None = None,
                         has_header: bool = True) -> Table:
        """Create a data table with optional styling."""
        table = Table(data, colWidths=col_widths)
        
        style_commands = [
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]
        
        if has_header and data:
            style_commands.extend([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ])
        
        table.setStyle(TableStyle(style_commands))
        return table
    
    def format_currency(self, amount: float, symbol: str = "$", format_str: str = ",.2f") -> str:
        """Format currency amount."""
        return f"{symbol}{amount:{format_str}}"
    
    def format_date(self, date_value: Any, format_str: str = "%m/%d/%Y") -> str:
        """Format date value."""
        if pd.isna(date_value):
            return datetime.now().strftime(format_str)
        
        if isinstance(date_value, str):
            try:
                date_value = pd.to_datetime(date_value)
            except:
                return str(date_value)
        
        if hasattr(date_value, 'strftime'):
            return date_value.strftime(format_str)
        
        return str(date_value)
    
    @staticmethod
    def merge_pdfs(file_list: list[str], output_path: str) -> None:
        """Merge multiple PDF files into one."""
        writer = PdfWriter()
        
        for filepath in file_list:
            try:
                reader = PdfReader(filepath)
                for page in reader.pages:
                    writer.add_page(page)
            except Exception as e:
                logger.error(f"Error reading PDF {filepath}: {e}")
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
