# mergedoc_generator/core/__init__.py
"""
Core components for the merged document generator.
"""

from mergedoc_generator.core.base import DocumentGenerator, DocumentConfig
from mergedoc_generator.core.data_loader import DataLoader
from mergedoc_generator.core.pdf_builder import PDFBuilder

__all__ = ['DocumentGenerator', 'DocumentConfig', 'DataLoader', 'PDFBuilder']
