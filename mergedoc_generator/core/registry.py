# mergedoc_generator/core/registry.py
"""
Registry for document type plugins.
"""

from typing import Any
import logging

logger = logging.getLogger(__name__)


class DocumentTypeRegistry:
    """Registry for managing document type plugins."""
    
    _document_types: dict[str, dict[str, Any]] = {}
    
    @classmethod
    def register(cls, name: str, info: dict[str, Any]) -> None:
        """Register a document type."""
        cls._document_types[name] = info
        logger.debug(f"Registered document type: {name}")
    
    @classmethod
    def get_all(cls) -> dict[str, dict[str, Any]]:
        """Get all registered document types."""
        return cls._document_types.copy()
    
    @classmethod
    def get(cls, name: str) -> dict[str, Any] | None:
        """Get a specific document type."""
        return cls._document_types.get(name)
