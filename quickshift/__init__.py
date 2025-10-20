"""
Quickshift - A Python-based DSL for local file-structure data manipulation.
"""

from quickshift.lexer.lexer import create_lexer, tokenize_file, tokenize_string

__version__ = "0.1.0"
__all__ = [
    "create_lexer",
    "tokenize_file",
    "tokenize_string",
]
