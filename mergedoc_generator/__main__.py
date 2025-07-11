
# mergedoc_generator/__main__.py
"""
Entry point for the mergedoc_generator package.
Allows execution with: python -m mergedoc_generator
"""

import sys
from mergedoc_generator.cli import main

if __name__ == '__main__':
    sys.exit(main())
