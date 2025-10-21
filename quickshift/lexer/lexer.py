"""
Lexer implementation for the Quickshift DSL using PLY.
"""

import ply.lex as lex

from quickshift.utils.errors import QuickshiftLexError

# ========================================================================
# Reserved keywords mapping lowercase to token names
# ========================================================================
RESERVED = {
    # Data Classifications
    "source": "SOURCE",
    "schema": "SCHEMA",
    "column": "COLUMN",
    "type": "TYPE",
    "path": "PATH",
    "table": "TABLE",
    "name": "NAME",
    "nullable": "NULLABLE",
    "True": "TRUE",
    "False": "FALSE",
    # SourceType Classifications
    "csv": "CSV",
    "parquet": "PARQUET",
    "postgres": "POSTGRES",
    # DataType Classifications
    "str": "STR",
    "int": "INT",
}

# Generate list of reserved keyword values for token list
RESERVED_TOKENS = list(RESERVED.values())

# ========================================================================
# Token list - combines reserved words with other tokens
# ========================================================================
tokens = [
    "IDENTIFIER",
    "EQUALS",
    "LPAREN",
    "RPAREN",
    "COMMA",
    "STRING",
    "NUMBER",
    "NEWLINE",
    "INDENT",
    "DEDENT",
] + RESERVED_TOKENS


class QuickshiftLexer:
    """
    Lexer for the Quickshift domain-specific language.
    Tokenizes Quickshift source code for parsing.
    """

    # Required by PLY
    tokens = tokens

    # ========================================================================
    # SIMPLE TOKEN RULES (using strings)
    # ========================================================================
    t_EQUALS = r"="
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_COMMA = r","

    # ========================================================================
    # COMPLEX TOKEN RULES (using functions)
    # ========================================================================

    def t_IDENTIFIER(self, t):
        r"[a-zA-Z_][a-zA-Z0-9_]*"
        t.type = RESERVED.get(t.value, "IDENTIFIER")
        return t

    def t_STRING(self, t):
        r'"[^"]*"'
        t.value = t.value[1:-1]  # Strip quotes

    def t_NUMBER(self, t):
        r"\d+"
        t.value = int(t.value)
        return t

    # Track line numbers and handle newlines
    def t_NEWLINE(t):
        r"\n+"
        t.lexer.lineno += len(t.value)
        return t

    # Ignore spaces (but not tabs - we'll handle indentation separately)
    t_ignore = " "

    def t_error(self, t):
        raise QuickshiftLexError(f"Illegal character '{t.value[0]}' (line {t.lineno})")

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)


class IndentLexer:
    def __init__(self):
        self.lexer = lex.lex()
        self.token_stream = None
        self.indent_stack = [0]

    def input(self, data):
        self.lexer.input(data)
        self.token_stream = self._process_indentation()

    def token(self):
        try:
            return next(self.token_stream)
        except StopIteration:
            return None

    def _process_indentation(self):
        """Process tokens and inject INDENT/DEDENT tokens"""
        tokens = []
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            tokens.append(tok)

        i = 0
        while i < len(tokens):
            tok = tokens[i]

            # At start of line (after NEWLINE), check indentation
            if i > 0 and tokens[i - 1].type == "NEWLINE":
                # Count leading spaces/tabs
                indent_level = 0
                if tok.type != "NEWLINE":  # Not an empty line
                    # Simple approach: assume 4 spaces = 1 indent level
                    # In production, you'd want proper tab/space handling
                    pass  # Indentation measured by position tracking

                # For simplicity, we'll skip complex indent handling in this example
                # and rely on explicit newlines for multi-line statements

            yield tok
            i += 1

        # Emit remaining DEDENTs
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            dedent_tok = lex.LexToken()
            dedent_tok.type = "DEDENT"
            dedent_tok.value = None
            dedent_tok.lineno = tokens[-1].lineno if tokens else 0
            dedent_tok.lexpos = tokens[-1].lexpos if tokens else 0
            yield dedent_tok
