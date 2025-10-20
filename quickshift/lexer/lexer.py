"""
Lexer implementation for the Quickshift DSL using PLY.
"""

import ply.lex as lex
from quickshift.lexer.tokens import tokens
from quickshift.lexer.reserved import RESERVED
from quickshift.utils.errors import QuickshiftLexError


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

    # Operators
    t_PLUS = r"\+"
    t_MINUS = r"-"
    t_MULTIPLY = r"\*"
    t_DIVIDE = r"/"
    t_MODULO = r"%"

    # Comparison operators
    t_EQUALS = r"=="
    t_NOT_EQUALS = r"!="
    t_LESS_EQUAL = r"<="
    t_GREATER_EQUAL = r">="
    t_LESS_THAN = r"<"
    t_GREATER_THAN = r">"

    # Assignment and special operators
    t_ASSIGN = r"="
    t_COLON = r":"
    t_DOUBLE_COLON = r"::"
    t_PIPELINE = r">>"
    t_DOT = r"\."
    t_ARROW = r"->"

    # Delimiters
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_LBRACKET = r"\["
    t_RBRACKET = r"\]"
    t_LBRACE = r"\{"
    t_RBRACE = r"\}"
    t_COMMA = r","
    t_SEMICOLON = r";"

    # Ignore spaces and tabs (but not newlines - they're significant)
    t_ignore = " \t"

    # ========================================================================
    # COMPLEX TOKEN RULES (using functions)
    # ========================================================================

    def t_COMMENT(self, t):
        r"\#.*"
        # Comments are ignored, so we don't return the token
        pass

    def t_FILE_PROTOCOL(self, t):
        r"file://"
        return t

    def t_S3_PROTOCOL(self, t):
        r"s3://"
        return t

    def t_GS_PROTOCOL(self, t):
        r"gs://"
        return t

    def t_WASBS_PROTOCOL(self, t):
        r"wasbs://"
        return t

    def t_FLOAT_LITERAL(self, t):
        r"\d+\.\d+"
        t.value = float(t.value)
        return t

    def t_INTEGER(self, t):
        r"\d+"
        t.value = int(t.value)
        return t

    def t_STRING_LITERAL(self, t):
        r'"([^"\\]|\\.)*"'
        # Remove quotes and handle escape sequences
        t.value = t.value[1:-1]  # Strip quotes
        t.value = t.value.replace("\\n", "\n")
        t.value = t.value.replace("\\t", "\t")
        t.value = t.value.replace('\\"', '"')
        t.value = t.value.replace("\\\\", "\\")
        return t

    def t_BOOLEAN(self, t):
        r"true|false|True|False"
        t.value = t.value.lower() == "true"
        return t

    def t_IDENTIFIER(self, t):
        r"[a-zA-Z_][a-zA-Z0-9_]*"
        # Check if identifier is a reserved word
        t.type = RESERVED.get(t.value, "IDENTIFIER")
        return t

    def t_NEWLINE(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)
        return t

    # ========================================================================
    # ERROR HANDLING
    # ========================================================================

    def t_error(self, t):
        """
        Error handling rule for illegal characters.
        """
        raise QuickshiftLexError(
            f"Illegal character '{t.value[0]}' at line {t.lineno}, position {t.lexpos}",
            line=t.lineno,
            position=t.lexpos,
            character=t.value[0],
        )

    # ========================================================================
    # LEXER CONSTRUCTION
    # ========================================================================

    def __init__(self, **kwargs):
        """
        Initialize the lexer.

        Args:
            **kwargs: Additional arguments passed to ply.lex.lex()
        """
        self.lexer = lex.lex(module=self, **kwargs)
        self.tokens_list = []  # Store tokenized output

    def tokenize(self, data, debug=False):
        """
        Tokenize input data.

        Args:
            data (str): Source code to tokenize
            debug (bool): If True, print tokens as they're generated

        Returns:
            list: List of tokens
        """
        self.lexer.input(data)
        self.tokens_list = []

        while True:
            tok = self.lexer.token()
            if not tok:
                break

            # Inject protocol tokens when a string literal starts with a known protocol prefix.
            # This follows the DSL design where storage protocol schemes are recognized as single tokens
            # even when they appear inside quoted paths, e.g., path="file://...".
            if tok.type == "STRING_LITERAL":
                val = tok.value
                proto_map = {
                    "file://": "FILE_PROTOCOL",
                    "s3://": "S3_PROTOCOL",
                    "gs://": "GS_PROTOCOL",
                    "wasbs://": "WASBS_PROTOCOL",
                    # ToDo: Add more protocols
                }
                for prefix, ttype in proto_map.items():
                    if isinstance(val, str) and val.startswith(prefix):
                        # Create a synthetic protocol token to reflect the protocol prefix
                        # while keeping the original string literal token as-is.
                        ptok = lex.LexToken()
                        ptok.type = ttype
                        ptok.value = prefix
                        ptok.lineno = tok.lineno
                        ptok.lexpos = tok.lexpos
                        self.tokens_list.append(ptok)
                        if debug:
                            print(
                                f"{ptok.type:20s} {repr(ptok.value):30s} Line: {ptok.lineno:4d} Pos: {ptok.lexpos:5d}"
                            )
                        break

            self.tokens_list.append(tok)

            if debug:
                print(
                    f"{tok.type:20s} {repr(tok.value):30s} Line: {tok.lineno:4d} Pos: {tok.lexpos:5d}"
                )

        return self.tokens_list

    def input(self, data):
        """
        Set input data for the lexer.

        Args:
            data (str): Source code to tokenize
        """
        self.lexer.input(data)

    def token(self):
        """
        Get the next token.

        Returns:
            LexToken or None: Next token or None if no more tokens
        """
        return self.lexer.token()

    def reset_lineno(self):
        """
        Reset line number counter.
        """
        self.lexer.lineno = 1


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def create_lexer(**kwargs):
    """
    Factory function to create a Quickshift lexer instance.

    Args:
        **kwargs: Additional arguments passed to QuickshiftLexer

    Returns:
        QuickshiftLexer: Configured lexer instance
    """
    return QuickshiftLexer(**kwargs)


def tokenize_file(filepath, debug=False):
    """
    Tokenize a Quickshift source file.

    Args:
        filepath (str): Path to .qs file
        debug (bool): If True, print tokens as they're generated

    Returns:
        list: List of tokens
    """
    lexer = create_lexer()

    with open(filepath, "r", encoding="utf-8") as f:
        data = f.read()

    return lexer.tokenize(data, debug=debug)


def tokenize_string(source_code, debug=False):
    """
    Tokenize a Quickshift source code string.

    Args:
        source_code (str): Quickshift source code
        debug (bool): If True, print tokens as they're generated

    Returns:
        list: List of tokens
    """
    lexer = create_lexer()
    return lexer.tokenize(source_code, debug=debug)
