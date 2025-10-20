"""
Token definitions for the Quickshift DSL lexer.
"""

from quickshift.lexer.reserved import RESERVED_TOKENS

# Token list - combines reserved words with other tokens
tokens = [
    # Identifiers and literals
    "IDENTIFIER",
    "INTEGER",
    "FLOAT_LITERAL",
    "STRING_LITERAL",
    "BOOLEAN",
    # Operators
    "PLUS",
    "MINUS",
    "MULTIPLY",
    "DIVIDE",
    "MODULO",
    # Comparison operators
    "EQUALS",
    "NOT_EQUALS",
    "LESS_THAN",
    "GREATER_THAN",
    "LESS_EQUAL",
    "GREATER_EQUAL",
    # Assignment and special operators
    "ASSIGN",
    "COLON",
    "DOUBLE_COLON",
    "PIPELINE",  # >>
    "DOT",
    "ARROW",  # ->
    # Delimiters
    "LPAREN",
    "RPAREN",
    "LBRACKET",
    "RBRACKET",
    "LBRACE",
    "RBRACE",
    "COMMA",
    "SEMICOLON",
    # File protocol prefixes (as single tokens)
    "FILE_PROTOCOL",  # file://
    "S3_PROTOCOL",  # s3://
    "GS_PROTOCOL",  # gs://
    "WASBS_PROTOCOL",  # wasbs://
    # Special
    "NEWLINE",
    "COMMENT",
] + RESERVED_TOKENS

# Token rules are defined in lexer.py
