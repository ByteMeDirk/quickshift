"""
Quickshift - A Python-based DSL for data management
"""

__version__ = "0.1.0"

from .lexer import Lexer
from .parser import Parser
from .semantic_analyzer import SemanticAnalyzer
from .codegen import CodeGenerator

__all__ = ["Lexer", "Parser", "SemanticAnalyzer", "CodeGenerator"]
