# mergedoc_generator/core/base.py
"""
Base classes and interfaces for document generation.
"""

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
import logging

logger = logging.getLogger(__name__)


class DocumentConfig:
    """Base configuration class for document formatting and layout."""

    def __init__(self, config_file: str | None = None):
        self.config = self.get_default_config()

        # Try to load config from multiple locations
        config_loaded = False

        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
            config_loaded = True
        else:
            # Try standard config locations
            for config_path in self._get_config_search_paths():
                if config_path.exists():
                    self.load_config(str(config_path))
                    config_loaded = True
                    break

        if not config_loaded:
            logger.info("No configuration file found. Using defaults. Run with --create-samples to generate templates.")

    def _get_config_search_paths(self) -> list[Path]:
        """Get list of paths to search for configuration files."""
        import platform

        config_name = f"{self.config.get('document_type', 'document')}_config.json"
        paths = []

        # Current working directory (highest priority after --config)
        paths.append(Path.cwd() / config_name)

        # Platform-specific user config directories
        home = Path.home()
        system = platform.system().lower()

        if system == "windows":
            # Windows: %APPDATA%\mergedoc_generator\
            appdata = os.environ.get('APPDATA')
            if appdata:
                paths.append(Path(appdata) / "mergedoc_generator" / config_name)
            # Fallback to user home
            paths.append(home / "AppData" / "Roaming" / "mergedoc_generator" / config_name)

        elif system == "darwin":  # macOS
            # macOS: ~/Library/Application Support/mergedoc_generator/
            paths.append(home / "Library" / "Application Support" / "mergedoc_generator" / config_name)

        else:  # Linux and other Unix-like systems
            # XDG config directory if available
            xdg_config = os.environ.get('XDG_CONFIG_HOME')
            if xdg_config:
                paths.append(Path(xdg_config) / "mergedoc_generator" / config_name)
            # Standard XDG location
            paths.append(home / ".config" / "mergedoc_generator" / config_name)

        # Cross-platform fallback in user home directory
        paths.append(home / ".mergedoc_generator" / config_name)

        return paths

    def get_default_config(self) -> dict[str, Any]:
        """Get default configuration. Override in subclasses."""
        return {
            "page_size": "letter",
            "margins": {"top": 72, "bottom": 72, "left": 72, "right": 72},
            "company": {
                "name": "[COMPANY NAME - CONFIGURE ME]",
                "address": "[COMPANY ADDRESS\nCITY, STATE ZIP - CONFIGURE ME]",
                "phone": "[PHONE NUMBER - CONFIGURE ME]",
                "email": "[EMAIL - CONFIGURE ME]"
            },
            "output": {
                "individual_files": True,
                "merged_file": False,
                "output_directory": "generated_documents",
                "filename_template": "document_{document_number}.pdf"
            }
        }

    def load_config(self, config_file: str) -> None:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                self._update_nested_dict(self.config, user_config)
            logger.info(f"Configuration loaded from {config_file}")
        except Exception as e:
            logger.error(f"Error loading config file {config_file}: {e}")

    def save_config_template(self, location: str = "user") -> Path:
        """Save a configuration template to a standard location.

        Args:
            location: Where to save ('user', 'local', or specific path)

        Returns:
            Path where the config was saved
        """
        config_name = f"{self.config.get('document_type', 'document')}_config.json"

        if location == "user":
            # Save to user's config directory
            config_dir = Path.home() / ".config" / "mergedoc_generator"
            config_dir.mkdir(parents=True, exist_ok=True)
            config_path = config_dir / config_name
        elif location == "local":
            # Save to current directory
            config_path = Path.cwd() / config_name
        else:
            # Save to specific path
            config_path = Path(location) / config_name
            config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create a clean template config (remove any loaded customizations)
        template_config = self.get_default_config()

        with open(config_path, 'w') as f:
            json.dump(template_config, f, indent=2)

        logger.info(f"Configuration template saved to: {config_path}")
        return config_path

    def _update_nested_dict(self, base_dict: dict[str, Any], update_dict: dict[str, Any]) -> None:
        """Recursively update nested dictionary."""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._update_nested_dict(base_dict[key], value)
            else:
                base_dict[key] = value


class DocumentGenerator(ABC):
    """Abstract base class for document generators."""

    def __init__(self, config: DocumentConfig):
        self.config = config.config

    @abstractmethod
    def generate_documents(self, data, document_range: list[str] | None = None) -> list[str]:
        """Generate documents from data. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def _group_document_data(self, data, document_field: str) -> dict[str, Any]:
        """Group data by document identifier. Must be implemented by subclasses."""
        pass

    def _generate_filename(self, document_number: str) -> str:
        """Generate filename for document."""
        template = self.config['output']['filename_template']
        return template.format(document_number=document_number)

    def _create_output_directory(self) -> Path:
        """Create and return output directory."""
        output_dir = Path(self.config['output']['output_directory'])
        output_dir.mkdir(exist_ok=True)
        return output_dir
