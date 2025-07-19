# mergedoc_generator/document_types/layout_demo.py
"""
Layout Demo document type - demonstrates all positioning and layout techniques.
"""

import pandas as pd
import json
from datetime import datetime
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
from reportlab.platypus import Spacer, Paragraph, Table, TableStyle, Image, KeepTogether
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF
from reportlab.platypus.flowables import Flowable

import logging
logger = logging.getLogger(__name__)


def get_document_info() -> dict[str, Any]:
    """Get information about this document type."""
    return {
        "display_name": "Layout Demo",
        "description": "Demonstrates all layout techniques with visible borders for testing",
        "version": "1.0.0"
    }


class DebugRect(Flowable):
    """Custom flowable that draws a colored rectangle for layout debugging."""
    
    def __init__(self, width, height, color=colors.lightblue, label=""):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.color = color
        self.label = label
    
    def draw(self):
        """Draw the rectangle on the canvas."""
        self.canv.setFillColor(self.color)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=1)
        if self.label:
            self.canv.setFillColor(colors.black)
            self.canv.drawString(5, self.height - 15, self.label)


class DocumentConfig(BaseDocumentConfig):
    """Layout Demo configuration."""
    
    def get_default_config(self) -> dict[str, Any]:
        """Get default layout demo configuration."""
        base_config: dict[str: Any] = super().get_default_config()
        
        demo_config = {
            "document_type": "layout_demo",
            "debug_mode": True,  # Show visible borders and guides
            "company": {
                "name": "[DEMO COMPANY]",
                "address": "[DEMO ADDRESS]",
                "phone": "[DEMO PHONE]",
                "email": "[DEMO EMAIL]"
            },
            "fields": {
                "document_number_field": "demo_number",
                "customer_fields": ["demo_customer"],
                "line_item_fields": ["demo_item", "demo_qty", "demo_price"],
            },
            "output": {
                "individual_files": True,
                "merged_file": False,
                "output_directory": "layout_demos",
                "filename_template": "layout_demo_{document_number}.pdf"
            }
        }
        
        base_config.update(demo_config)
        return base_config


class DocumentGenerator(BaseDocumentGenerator):
    """Layout Demo document generator."""
    
    def __init__(self, config: DocumentConfig):
        super().__init__(config)

        self.pdf_builder = PDFBuilder(self.config)
        self.debug_mode = self.config.get('debug_mode', False)
        
        # Colors for different layout areas when debugging
        self.debug_colors = {
            'header': colors.lightblue,
            'content': colors.lightgreen, 
            'sidebar': colors.lightyellow,
            'footer': colors.lightcoral,
            'table': colors.lightgrey
        }
    
    def generate_documents(self, data: pd.DataFrame, document_range: list[str] | None = None) -> list[str]:
        """Generate layout demo documents."""
        generated_files = []
        output_dir = self._create_output_directory()
        
        # Create a single demo document
        filename = "layout_demo_showcase.pdf"
        filepath = output_dir / filename
        
        self._create_demo_pdf(str(filepath))
        generated_files.append(str(filepath))
        logger.info(f"Generated layout demo: {filepath}")
        
        return generated_files
    
    def _group_document_data(self, data: pd.DataFrame, document_field: str) -> dict[str, pd.DataFrame]:
        """Not used for demo, but required by base class."""
        return {"demo": data}
    
    def _get_debug_style(self, area_type: str = 'content') -> list:
        """Get table style with optional visible borders for debugging."""
        base_style = [
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]
        
        if self.debug_mode:
            base_style.extend([
                ('GRID', (0, 0), (-1, -1), 2, colors.red),  # Visible red borders
                ('BACKGROUND', (0, 0), (-1, -1), self.debug_colors.get(area_type, colors.white)),
            ])
        else:
            base_style.append(('GRID', (0, 0), (-1, -1), 0, colors.white))  # Invisible
        
        return base_style
    
    def _create_demo_pdf(self, filepath: str) -> None:
        """Create a comprehensive layout demonstration PDF."""
        story = []
        
        # Title
        title = Paragraph("<b>LAYOUT DEMO - All Positioning Techniques</b>", 
                            self.pdf_builder.styles['DocumentTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        if self.debug_mode:
            debug_note = Paragraph(
                "<i>DEBUG MODE: Red borders show table boundaries, colored backgrounds show layout areas</i>",
                self.pdf_builder.styles['Normal']
            )
            story.append(debug_note)
            story.append(Spacer(1, 20))
        
        # 1. BASIC TWO-COLUMN LAYOUT
        story.append(Paragraph("<b>1. Two-Column Layout (Header Style)</b>", 
                                self.pdf_builder.styles['Heading2']))
        story.extend(self._demo_two_column_layout())
        story.append(Spacer(1, 20))
        
        # 2. THREE-COLUMN LAYOUT  
        story.append(Paragraph("<b>2. Three-Column Layout</b>", 
                                self.pdf_builder.styles['Heading2']))
        story.extend(self._demo_three_column_layout())
        story.append(Spacer(1, 20))
        
        # 3. NESTED TABLES
        story.append(Paragraph("<b>3. Nested Tables for Complex Layouts</b>", 
                                self.pdf_builder.styles['Heading2']))
        story.extend(self._demo_nested_tables())
        story.append(Spacer(1, 20))
        
        # 4. MIXED CONTENT POSITIONING
        story.append(Paragraph("<b>4. Mixed Content (Text, Tables, Images)</b>", 
                                self.pdf_builder.styles['Heading2']))
        story.extend(self._demo_mixed_content())
        story.append(Spacer(1, 20))
        
        # 5. ALIGNMENT TECHNIQUES
        story.append(Paragraph("<b>5. Alignment Techniques</b>", 
                                self.pdf_builder.styles['Heading2']))
        story.extend(self._demo_alignment_techniques())
        story.append(Spacer(1, 20))
        
        # 6. SPACING AND PADDING
        story.append(Paragraph("<b>6. Spacing and Padding Control</b>", 
                                self.pdf_builder.styles['Heading2']))
        story.extend(self._demo_spacing_control())
        story.append(Spacer(1, 20))
        
        # 7. OVERLAPPING ELEMENTS (Pseudo-overlapping)
        story.append(Paragraph("<b>7. Pseudo-Overlapping Elements</b>", 
                                self.pdf_builder.styles['Heading2']))
        story.extend(self._demo_overlapping_elements())
        
        self.pdf_builder.create_document(filepath, story)
    
    def _demo_two_column_layout(self) -> list[Any]:
        """Demonstrate basic two-column layout."""
        left_content = """
        <b>Left Column</b><br/>
        This is the left side content.<br/>
        • Company information<br/>
        • Contact details<br/>
        • Address information
        """
        
        right_content = """
        <b>Right Column</b><br/>
        This is the right side content.<br/>
        • Invoice details<br/>
        • Date information<br/>
        • Document numbers
        """
        
        table = Table([
            [   Paragraph(left_content, self.pdf_builder.styles['Normal']),
                Paragraph(right_content, self.pdf_builder.styles['Normal'])]
        ], colWidths=[3*inch, 3*inch])
        
        table.setStyle(TableStyle(self._get_debug_style('header')))
        
        return [table]
    
    def _demo_three_column_layout(self) -> list[Any]:
        """Demonstrate three-column layout."""
        col1 = Paragraph("<b>Column 1</b><br/>Left content", self.pdf_builder.styles['Normal'])
        col2 = Paragraph("<b>Column 2</b><br/>Center content", self.pdf_builder.styles['Normal'])
        col3 = Paragraph("<b>Column 3</b><br/>Right content", self.pdf_builder.styles['Normal'])
        
        table = Table([
            [col1, col2, col3]
        ], colWidths=[2*inch, 2*inch, 2*inch])
        
        table.setStyle(TableStyle(self._get_debug_style('content')))
        
        return [table]
    
    def _demo_nested_tables(self) -> list[Any]:
        """Demonstrate nested tables for complex layouts."""
        # Inner table
        inner_table = Table([
            ["Item A", "10", "$50"],
            ["Item B", "5", "$25"]
        ], colWidths=[1*inch, 0.5*inch, 0.5*inch])
        
        inner_style = self._get_debug_style('table')
        inner_style.append(('FONTSIZE', (0, 0), (-1, -1), 8))
        inner_table.setStyle(TableStyle(inner_style))
        
        # Outer table containing the inner table
        outer_table = Table([
            ["Description", inner_table],
            ["Notes", Paragraph("This shows how tables can be nested", 
                                self.pdf_builder.styles['Normal'])]
        ], colWidths=[1.5*inch, 3*inch])
        
        outer_table.setStyle(TableStyle(self._get_debug_style('content')))
        
        return [outer_table]
    
    def _demo_mixed_content(self) -> list[Any]:
        """Demonstrate mixing different content types."""
        # Create a placeholder "image" using a colored rectangle
        fake_image = DebugRect(1*inch, 0.8*inch, colors.lightblue, "IMAGE AREA")
        
        text_content = Paragraph(
            "This demonstrates how to mix images, text, and tables in the same layout area.",
            self.pdf_builder.styles['Normal']
        )
        
        # Table mixing different content types
        mixed_table = Table([
            [fake_image, text_content]
        ], colWidths=[1.2*inch, 4*inch])
        
        mixed_table.setStyle(TableStyle(self._get_debug_style('content')))
        
        return [mixed_table]
    
    def _demo_alignment_techniques(self) -> list[Any]:
        """Demonstrate different alignment options."""
        elements = []
        
        # Different alignments in table cells
        align_table = Table([
            [   Paragraph("Left Aligned", self.pdf_builder.styles['Normal']),
                Paragraph("Center Aligned", self.pdf_builder.styles['Normal']),
                Paragraph("Right Aligned", self.pdf_builder.styles['Normal'])]
        ], colWidths=[2*inch, 2*inch, 2*inch])
        
        align_style = self._get_debug_style('content')
        align_style.extend([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'), 
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ])
        align_table.setStyle(TableStyle(align_style))
        
        elements.append(align_table)
        elements.append(Spacer(1, 10))
        
        # Vertical alignment demo
        valign_table = Table([
            [   Paragraph("Top aligned content", self.pdf_builder.styles['Normal']),
                Paragraph("Middle aligned<br/>multiline<br/>content", self.pdf_builder.styles['Normal']),
                Paragraph("Bottom aligned", self.pdf_builder.styles['Normal'])]
        ], colWidths=[2*inch, 2*inch, 2*inch], rowHeights=[0.8*inch])
        
        valign_style = self._get_debug_style('sidebar')
        valign_style.extend([
            ('VALIGN', (0, 0), (0, 0), 'TOP'),
            ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),
            ('VALIGN', (2, 0), (2, 0), 'BOTTOM'),
        ])
        valign_table.setStyle(TableStyle(valign_style))
        
        elements.append(valign_table)
        
        return elements
    
    def _demo_spacing_control(self) -> list[Any]:
        """Demonstrate spacing and padding control."""
        elements = []
        
        # Different padding examples
        padding_table = Table([
            ["No Padding", "Normal Padding", "Extra Padding"]
        ], colWidths=[2*inch, 2*inch, 2*inch])
        
        padding_style = self._get_debug_style('content')
        padding_style.extend([
            # No padding on first cell
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (0, 0), (0, 0), 0),
            ('TOPPADDING', (0, 0), (0, 0), 0),
            ('BOTTOMPADDING', (0, 0), (0, 0), 0),
            
            # Extra padding on third cell
            ('LEFTPADDING', (2, 0), (2, 0), 20),
            ('RIGHTPADDING', (2, 0), (2, 0), 20),
            ('TOPPADDING', (2, 0), (2, 0), 15),
            ('BOTTOMPADDING', (2, 0), (2, 0), 15),
        ])
        padding_table.setStyle(TableStyle(padding_style))
        
        elements.append(padding_table)
        elements.append(Spacer(1, 15))
        
        # Spacer demonstration
        elements.append(Paragraph("↑ 15pt Spacer above", self.pdf_builder.styles['Normal']))
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("↑ 30pt Spacer above", self.pdf_builder.styles['Normal']))
        elements.append(Spacer(1, 5))
        elements.append(Paragraph("↑ 5pt Spacer above", self.pdf_builder.styles['Normal']))
        
        return elements
    
    def _demo_overlapping_elements(self) -> list[Any]:
        """Demonstrate pseudo-overlapping using negative margins."""
        elements = []
        
        # Note about ReportLab limitations
        note = Paragraph(
            "<i>Note: ReportLab is flow-based, not absolute positioning. "
            "True overlapping requires custom canvas drawing. Here we show "
            "techniques for tight positioning that simulate overlapping.</i>",
            self.pdf_builder.styles['Normal']
        )
        elements.append(note)
        elements.append(Spacer(1, 10))
        
        # Tight spacing example
        tight_table1 = Table([
            ["First Element"]
        ], colWidths=[3*inch])
        tight_table1.setStyle(TableStyle(self._get_debug_style('header')))
        
        tight_table2 = Table([
            ["Second Element (tight spacing)"]
        ], colWidths=[3*inch])
        tight_table2.setStyle(TableStyle(self._get_debug_style('footer')))
        
        elements.append(tight_table1)
        elements.append(Spacer(1, 2))  # Very tight spacing
        elements.append(tight_table2)
        
        return elements


def create_sample_config() -> None:
    """Create a sample configuration file for layout demos."""
    sample_config = {
        "document_type": "layout_demo",
        "debug_mode": True,  # Set to False to hide borders
        "page_size": "letter",
        "margins": {"top": 72, "bottom": 72, "left": 72, "right": 72},
        "output": {
            "individual_files": True,
            "output_directory": "layout_demos",
            "filename_template": "layout_demo.pdf"
        }
    }
    
    with open('layout_demo_config.json', 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print("Layout demo configuration created: layout_demo_config.json")
    print("💡 Set 'debug_mode': false to hide borders and backgrounds")


def create_sample_data() -> None:
    """Create minimal sample data for layout demo."""
    sample_data = {
        'demo_number': ['DEMO-001'],
        'demo_customer': ['Demo Customer'],
        'demo_item': ['Demo Item'],
        'demo_qty': [1],
        'demo_price': [100.00]
    }
    
    df = pd.DataFrame(sample_data)
    df.to_csv('layout_demo_data.csv', index=False)
    
    print("Layout demo data created: layout_demo_data.csv")
