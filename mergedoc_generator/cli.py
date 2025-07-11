# mergedoc_generator/cli.py
"""
Command line interface for the merged document generator.
"""

import argparse
import importlib
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

from mergedoc_generator.core.data_loader import DataLoader
from mergedoc_generator.core.registry import DocumentTypeRegistry

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def discover_document_types() -> dict[str, str]:
    """Discover available document type modules."""
    document_types = {}
    
    # Get the document_types directory
    current_dir = Path(__file__).parent
    doc_types_dir = current_dir / 'document_types'
    
    if not doc_types_dir.exists():
        return document_types
    
    # Find all Python files in document_types directory
    for py_file in doc_types_dir.glob('*.py'):
        if py_file.name.startswith('__'):
            continue
        
        module_name = py_file.stem
        try:
            # Try to import the module to see if it's valid
            module_path = f'mergedoc_generator.document_types.{module_name}'
            module = importlib.import_module(module_path)
            
            # Check if it has the required components
            if hasattr(module, 'get_document_info'):
                info = module.get_document_info()
                document_types[module_name] = info.get('display_name', module_name.title())
            else:
                document_types[module_name] = module_name.title()
                
        except Exception as e:
            logger.warning(f"Could not load document type {module_name}: {e}")
    
    return document_types


def setup_user_config(doc_type: str, location: str = "user") -> None:
    """Set up user configuration files."""
    try:
        module_path = f'mergedoc_generator.document_types.{doc_type}'
        module = importlib.import_module(module_path)
        
        if hasattr(module, 'DocumentConfig'):
            config = module.DocumentConfig()
            config_path = config.save_config_template(location)
            
            print(f"✅ Configuration template created: {config_path}")
            print(f"📝 Please edit this file to customize your {doc_type} settings.")
            print(f"🏢 Make sure to update the company information!")
            
        if hasattr(module, 'create_sample_data'):
            module.create_sample_data()
            print(f"📊 Sample data files created for testing.")
            
    except Exception as e:
        logger.error(f"Error setting up config for {doc_type}: {e}")


def list_config_locations(doc_type: str) -> None:
    """List where configuration files are searched for."""
    try:
        module_path = f'mergedoc_generator.document_types.{doc_type}'
        module = importlib.import_module(module_path)
        
        if hasattr(module, 'DocumentConfig'):
            config = module.DocumentConfig()
            search_paths = config._get_config_search_paths()
            
            print(f"Configuration search paths for {doc_type}:")
            for i, path in enumerate(search_paths, 1):
                exists = "✅" if path.exists() else "❌"
                print(f"  {i}. {exists} {path}")
                
    except Exception as e:
        logger.error(f"Error listing config locations for {doc_type}: {e}")


def create_sample_files(doc_type: str) -> None:
    """Create sample configuration and data files for a document type."""
    try:
        module_path = f'mergedoc_generator.document_types.{doc_type}'
        module = importlib.import_module(module_path)
        
        if hasattr(module, 'create_sample_config'):
            module.create_sample_config()
        
        if hasattr(module, 'create_sample_data'):
            module.create_sample_data()
            
        print(f"Sample files created for {doc_type}")
        
    except Exception as e:
        logger.error(f"Error creating sample files for {doc_type}: {e}")


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate merged documents from data files',
        prog='mergedoc_generator'
    )
    
    # Discover available document types
    doc_types = discover_document_types()
    
    if not doc_types:
        print("No document types found. Please check your installation.")
        return 1
    
    parser.add_argument('--type', '-t', 
                       choices=list(doc_types.keys()),
                       required=True,
                       help=f"Document type: {', '.join(f'{k} ({v})' for k, v in doc_types.items())}")
    
    parser.add_argument('--source', '-s',
                       help='Source data file (Excel, CSV, or TSV)')
    
    parser.add_argument('--config', '-c',
                       help='Configuration file (JSON)')
    
    parser.add_argument('--range', '-r', nargs='*',
                       help='Specific document numbers to generate')
    
    parser.add_argument('--list-types', action='store_true',
                       help='List available document types and exit')
    
    parser.add_argument('--setup', action='store_true',
                       help='Set up configuration files for a document type')
    
    parser.add_argument('--setup-location', choices=['user', 'local'],
                       default='user',
                       help='Where to create config files (user: ~/.config, local: current dir)')
    
    parser.add_argument('--list-configs', action='store_true',
                       help='List configuration file locations and their status')
    
    parser.add_argument('--create-samples', action='store_true',
                       help='Create sample configuration and data files (legacy)')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.list_types:
        print("Available document types:")
        for key, name in doc_types.items():
            print(f"  {key}: {name}")
        print(f"\nTo get started:")
        print(f"  python -m mergedoc_generator --type <type> --setup")
        return 0
    
    if args.setup:
        if not args.type:
            print("Please specify a document type with --type")
            print("Use --list-types to see available types")
            return 1
        setup_user_config(args.type, args.setup_location)
        return 0
    
    if args.list_configs:
        if not args.type:
            print("Please specify a document type with --type")
            return 1
        list_config_locations(args.type)
        return 0
    
    if args.create_samples:
        if not args.type:
            print("Please specify a document type with --type")
            return 1
        create_sample_files(args.type)
        return 0
    
    if not args.source:
        print("Source data file is required. Use --source to specify.")
        return 1
    
    try:
        # Load the specific document type module
        module_path = f'mergedoc_generator.document_types.{args.type}'
        doc_module = importlib.import_module(module_path)
        
        # Get the document generator class
        if not hasattr(doc_module, 'DocumentGenerator'):
            raise ImportError(f"Document type {args.type} missing DocumentGenerator class")
        
        GeneratorClass = doc_module.DocumentGenerator
        
        # Load configuration
        if hasattr(doc_module, 'DocumentConfig'):
            config = doc_module.DocumentConfig(args.config)
        else:
            from mergedoc_generator.core.base import DocumentConfig
            config = DocumentConfig(args.config)
        
        # Load data
        data = DataLoader.load_data(args.source)
        
        # Generate documents
        generator = GeneratorClass(config)
        generated_files = generator.generate_documents(data, args.range)
        
        print(f"\nSuccessfully generated {len(generated_files)} document files:")
        for file in generated_files:
            print(f"  - {file}")
        
    except Exception as e:
        logger.error(f"Error generating documents: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
