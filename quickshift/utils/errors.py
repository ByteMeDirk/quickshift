"""
Error handling for Quickshift DSL.
"""


class QuickshiftError(Exception):
    """Base exception for all Quickshift errors."""

    pass


class QuickshiftLexError(QuickshiftError):
    """Lexical analysis error."""

    def __init__(self, message, line=None, position=None, character=None):
        super().__init__(message)
        self.line = line
        self.position = position
        self.character = character

    def __str__(self):
        base_msg = super().__str__()
        if self.line is not None:
            return f"{base_msg}\n  at line {self.line}, position {self.position}"
        return base_msg


class QuickshiftParseError(QuickshiftError):
    """Parsing error."""

    def __init__(self, message, line=None, token=None):
        super().__init__(message)
        self.line = line
        self.token = token


class QuickshiftRuntimeError(QuickshiftError):
    """Runtime execution error."""

    pass


class QuickshiftTestError(QuickshiftError):
    """Test validation error."""

    def __init__(self, message, test_name=None, failures=None):
        super().__init__(message)
        self.test_name = test_name
        self.failures = failures or []
