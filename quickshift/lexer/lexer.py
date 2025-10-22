"""
Lexer implementation for the Quickshift DSL using PLY.
"""

import ply.lex as lex

from quickshift.utils.errors import QuickshiftLexError

# ========================================================================
# Reserved keywords mapping lowercase to token names
# ========================================================================
RESERVED = {
    # Language constructs
    "source": "SOURCE",
    "schema": "SCHEMA",
    "column": "COLUMN",
    "select": "SELECT",
    "from": "FROM",
    "True": "TRUE",
    "False": "FALSE",
}

# Generate list of reserved keyword values for token list
RESERVED_TOKENS = list(RESERVED.values())

# ========================================================================
# Token list - combines reserved words with other tokens
# ========================================================================
TOKENS = [
             "IDENTIFIER",
             "EQUALS",
             "LPAREN",
             "RPAREN",
             "COMMA",
             "STRING",
             "NUMBER",
             "NEWLINE",
             "SEMICOLON",  # Statement Termination
             "ASTERISK",
         ] + RESERVED_TOKENS


class QuickshiftLexer:
    """
    Lexer for the Quickshift domain-specific language.
    Tokenizes Quickshift source code for parsing.
    """

    # Required by PLY
    tokens = TOKENS

    # ========================================================================
    # SIMPLE TOKEN RULES (using strings)
    # ========================================================================
    t_EQUALS = r"="
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_COMMA = r","
    t_SEMICOLON = r";"
    t_ASTERISK = r"\*"

    # Ignore spaces (but not tabs - handled in indentation)
    t_ignore = " \t"

    # ========================================================================
    # COMPLEX TOKEN RULES (using functions)
    # ========================================================================

    def t_IDENTIFIER(self, t):
        r"[a-zA-Z_][a-zA-Z0-9_]*"
        # Only reserve actual language keywords
        t.type = RESERVED.get(t.value, "IDENTIFIER")
        return t

    def t_STRING(self, t):
        r"'[^']*'"
        t.value = t.value[1:-1]  # Strip quotes
        return t

    def t_NUMBER(self, t):
        r"\d+"
        t.value = int(t.value)
        return t

    def t_NEWLINE(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)
        return t

    def t_error(self, t):
        raise QuickshiftLexError(
            f"Illegal character '{t.value[0]}'",
            line=t.lineno,
            position=t.lexpos,
            character=t.value[0]
        )

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def input(self, data):
        """Pass input to the lexer."""
        self.lexer.input(data)

    def token(self):
        """Get the next token."""
        return self.lexer.token()


class IndentLexer:
    """
    Enhanced lexer that handles Python-style indentation.
    Emits INDENT and DEDENT tokens based on indentation levels.
    """

    def __init__(self):
        self.base_lexer = QuickshiftLexer()
        self.token_stream = None
        self.indent_stack = [0]

    def input(self, data):
        """Process input and prepare token stream with indentation."""
        self.base_lexer.input(data)
        self.token_stream = self._process_indentation()

    def token(self):
        """Get next token from the processed stream."""
        try:
            return next(self.token_stream)
        except StopIteration:
            return None

    def _process_indentation(self):
        """
        Process tokens and inject INDENT/DEDENT tokens based on indentation.
        Handles Python-style significant whitespace.
        """
        # Collect all tokens first
        tokens = []
        while True:
            tok = self.base_lexer.token()
            if not tok:
                break
            tokens.append(tok)

        # Process tokens with indentation awareness
        i = 0
        at_line_start = True

        while i < len(tokens):
            tok = tokens[i]

            # Handle line starts for indentation
            if at_line_start and tok.type not in ('NEWLINE', 'DEDENT', 'INDENT'):
                # Measure indentation (count spaces at line start)
                indent_level = self._measure_indent(tokens, i)

                # Generate INDENT or DEDENT tokens
                if indent_level > self.indent_stack[-1]:
                    self.indent_stack.append(indent_level)
                    indent_tok = self._create_token('INDENT', None, tok.lineno, tok.lexpos)
                    yield indent_tok
                elif indent_level < self.indent_stack[-1]:
                    while len(self.indent_stack) > 1 and indent_level < self.indent_stack[-1]:
                        self.indent_stack.pop()
                        dedent_tok = self._create_token('DEDENT', None, tok.lineno, tok.lexpos)
                        yield dedent_tok

                at_line_start = False

            # Handle newlines
            if tok.type == 'NEWLINE':
                at_line_start = True

            yield tok
            i += 1

        # Emit remaining DEDENTs at EOF
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            dedent_tok = self._create_token('DEDENT', None,
                                            tokens[-1].lineno if tokens else 0,
                                            tokens[-1].lexpos if tokens else 0)
            yield dedent_tok

    def _measure_indent(self, tokens, start_idx):
        """
        Measure indentation level at the start of a line.
        For now, assumes 4 spaces = 1 indent level.
        """
        # Simple implementation: actual indent tracking would need
        # to analyze the original source text positions
        return 0  # Placeholder - real implementation needed

    def _create_token(self, token_type, value, lineno, lexpos):
        """Create a new token."""
        tok = lex.LexToken()
        tok.type = token_type
        tok.value = value
        tok.lineno = lineno
        tok.lexpos = lexpos
        return tok
