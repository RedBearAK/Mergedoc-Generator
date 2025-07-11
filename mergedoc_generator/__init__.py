# mergedoc_generator/__init__.py
"""
Merged Document Generator

A flexible document generation system that creates PDFs from data sources
with support for repeating sections and complex layouts.
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from mergedoc_generator.core.base import DocumentGenerator, DocumentConfig
from mergedoc_generator.core.data_loader import DataLoader

__all__ = ['DocumentGenerator', 'DocumentConfig', 'DataLoader']
