# mergedoc_generator/core/data_loader.py
"""
Data loading utilities for various file formats.
"""

import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DataLoader:
    """Handles loading and processing data from various file formats."""
    
    @staticmethod
    def load_data(file_path: str) -> pd.DataFrame:
        """Load data from Excel, CSV, or TSV file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        extension = file_path.suffix.lower()
        
        try:
            if extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif extension == '.csv':
                df = pd.read_csv(file_path)
            elif extension in ['.tsv', '.txt']:
                df = pd.read_csv(file_path, sep='\t')
            else:
                raise ValueError(f"Unsupported file format: {extension}")
            
            logger.info(f"Loaded {len(df)} records from {file_path}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {e}")
            raise
