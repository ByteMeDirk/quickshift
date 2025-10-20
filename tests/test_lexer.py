"""
Unit tests for the Quickshift lexer.
"""

import pytest
from quickshift.lexer.lexer import QuickshiftLexer, tokenize_string
from quickshift.utils.errors import QuickshiftLexError


class TestLexerBasics:
    """Test basic lexer functionality."""

    def test_lexer_creation(self):
        """Test that lexer can be created."""
        lexer = QuickshiftLexer()
        assert lexer is not None
        assert lexer.lexer is not None

    def test_simple_identifier(self):
        """Test tokenizing a simple identifier."""
        lexer = QuickshiftLexer()
        tokens = lexer.tokenize("my_variable")

        assert len(tokens) == 1
        assert tokens[0].type == "IDENTIFIER"
        assert tokens[0].value == "my_variable"

    def test_reserved_keywords(self):
        """Test that reserved keywords are recognized."""
        lexer = QuickshiftLexer()
        tokens = lexer.tokenize("Source Sink Task Test")

        assert len(tokens) == 4
        assert tokens[0].type == "SOURCE"
        assert tokens[1].type == "SINK"
        assert tokens[2].type == "TASK"
        assert tokens[3].type == "TEST"


class TestLiterals:
    """Test literal value tokenization."""

    def test_integer(self):
        """Test integer tokenization."""
        tokens = tokenize_string("42 100 0")

        assert tokens[0].type == "INTEGER"
        assert tokens[0].value == 42
        assert tokens[1].value == 100
        assert tokens[2].value == 0

    def test_float(self):
        """Test float tokenization."""
        tokens = tokenize_string("3.14 0.5 100.0")

        assert tokens[0].type == "FLOAT_LITERAL"
        assert tokens[0].value == 3.14
        assert tokens[1].value == 0.5
        assert tokens[2].value == 100.0

    def test_string(self):
        """Test string tokenization."""
        tokens = tokenize_string('"hello world" "test"')

        assert tokens[0].type == "STRING_LITERAL"
        assert tokens[0].value == "hello world"
        assert tokens[1].value == "test"

    def test_string_escapes(self):
        """Test string escape sequences."""
        tokens = tokenize_string(r'"hello\nworld" "test\ttab" "quote\"here"')

        assert tokens[0].value == "hello\nworld"
        assert tokens[1].value == "test\ttab"
        assert tokens[2].value == 'quote"here'

    def test_boolean(self):
        """Test boolean tokenization."""
        tokens = tokenize_string("true false True False")

        assert all(t.type == "BOOLEAN" for t in tokens)
        assert tokens[0].value == True
        assert tokens[1].value == False
        assert tokens[2].value == True
        assert tokens[3].value == False


class TestOperators:
    """Test operator tokenization."""

    def test_arithmetic_operators(self):
        """Test arithmetic operator tokens."""
        tokens = tokenize_string("+ - * / %")

        assert tokens[0].type == "PLUS"
        assert tokens[1].type == "MINUS"
        assert tokens[2].type == "MULTIPLY"
        assert tokens[3].type == "DIVIDE"
        assert tokens[4].type == "MODULO"

    def test_comparison_operators(self):
        """Test comparison operator tokens."""
        tokens = tokenize_string("== != < > <= >=")

        assert tokens[0].type == "EQUALS"
        assert tokens[1].type == "NOT_EQUALS"
        assert tokens[2].type == "LESS_THAN"
        assert tokens[3].type == "GREATER_THAN"
        assert tokens[4].type == "LESS_EQUAL"
        assert tokens[5].type == "GREATER_EQUAL"

    def test_pipeline_operator(self):
        """Test pipeline operator."""
        tokens = tokenize_string("source >> sink")

        assert tokens[0].type == "IDENTIFIER"
        assert tokens[1].type == "PIPELINE"
        assert tokens[2].type == "IDENTIFIER"

    def test_assignment(self):
        """Test assignment operator."""
        tokens = tokenize_string("x = 5")

        assert tokens[0].type == "IDENTIFIER"
        assert tokens[1].type == "ASSIGN"
        assert tokens[2].type == "INTEGER"


class TestDelimiters:
    """Test delimiter tokenization."""

    def test_parentheses(self):
        """Test parenthesis tokens."""
        tokens = tokenize_string("()")

        assert tokens[0].type == "LPAREN"
        assert tokens[1].type == "RPAREN"

    def test_brackets(self):
        """Test bracket tokens."""
        tokens = tokenize_string("[]")

        assert tokens[0].type == "LBRACKET"
        assert tokens[1].type == "RBRACKET"

    def test_braces(self):
        """Test brace tokens."""
        tokens = tokenize_string("{}")

        assert tokens[0].type == "LBRACE"
        assert tokens[1].type == "RBRACE"

    def test_punctuation(self):
        """Test punctuation tokens."""
        tokens = tokenize_string(", : ;")

        assert tokens[0].type == "COMMA"
        assert tokens[1].type == "COLON"
        assert tokens[2].type == "SEMICOLON"


class TestProtocols:
    """Test file protocol tokenization."""

    def test_file_protocol(self):
        """Test file:// protocol."""
        tokens = tokenize_string("file://")
        assert tokens[0].type == "FILE_PROTOCOL"

    def test_s3_protocol(self):
        """Test s3:// protocol."""
        tokens = tokenize_string("s3://")
        assert tokens[0].type == "S3_PROTOCOL"

    def test_gs_protocol(self):
        """Test gs:// protocol."""
        tokens = tokenize_string("gs://")
        assert tokens[0].type == "GS_PROTOCOL"

    def test_wasbs_protocol(self):
        """Test wasbs:// protocol."""
        tokens = tokenize_string("wasbs://")
        assert tokens[0].type == "WASBS_PROTOCOL"


class TestComplexExpressions:
    """Test tokenization of complex expressions."""

    def test_source_declaration(self):
        """Test Source declaration tokenization."""
        code = 'my_source: Source(csv) = Source(path="file://data/*.csv")'
        tokens = tokenize_string(code)

        # Verify key tokens exist
        assert any(t.type == "IDENTIFIER" and t.value == "my_source" for t in tokens)
        assert any(t.type == "SOURCE" for t in tokens)
        assert any(t.type == "CSV" for t in tokens)
        assert any(t.type == "FILE_PROTOCOL" for t in tokens)

    def test_pipeline_operator_chain(self):
        """Test pipeline operator in context."""
        code = "source >> sink"
        tokens = tokenize_string(code)

        assert tokens[0].type == "IDENTIFIER"
        assert tokens[1].type == "PIPELINE"
        assert tokens[2].type == "IDENTIFIER"

    def test_method_chaining(self):
        """Test method chaining tokenization."""
        code = 'source.select("col1").where("col2" == "value")'
        tokens = tokenize_string(code)

        # Check structure
        assert any(t.type == "DOT" for t in tokens)
        assert any(t.type == "SELECT" for t in tokens)
        assert any(t.type == "WHERE" for t in tokens)

    def test_test_definition(self):
        """Test Test definition tokenization."""
        code = """
        my_test: Test = Test(
            target=my_source,
            checks=[not_null("id"), unique("email")]
        )
        """
        tokens = tokenize_string(code)

        assert any(t.type == "TEST" for t in tokens)
        assert any(t.type == "TARGET" for t in tokens)
        assert any(t.type == "CHECKS" for t in tokens)
        assert any(t.type == "NOT_NULL" for t in tokens)
        assert any(t.type == "UNIQUE" for t in tokens)


class TestComments:
    """Test comment handling."""

    def test_single_line_comment(self):
        """Test that comments are ignored."""
        code = """
        # This is a comment
        x = 5
        """
        tokens = tokenize_string(code)

        # Comment should not produce token
        assert not any(t.type == "COMMENT" for t in tokens)
        # But the assignment should still work
        assert any(t.type == "IDENTIFIER" for t in tokens)
        assert any(t.type == "ASSIGN" for t in tokens)

    def test_inline_comment(self):
        """Test inline comments."""
        code = "x = 5  # Assign 5 to x"
        tokens = tokenize_string(code)

        # Should only have assignment tokens, comment ignored
        assert len([t for t in tokens if t.type != "NEWLINE"]) == 3


class TestErrorHandling:
    """Test error handling."""

    def test_illegal_character(self):
        """Test that illegal characters raise errors."""
        lexer = QuickshiftLexer()

        with pytest.raises(QuickshiftLexError) as exc_info:
            lexer.tokenize("x = 5 @ y")

        assert "Illegal character" in str(exc_info.value)
        assert "@" in str(exc_info.value)

    def test_line_tracking(self):
        """Test that line numbers are tracked correctly."""
        code = """
        line1 = 1
        line2 = 2
        line3 = 3
        """
        tokens = tokenize_string(code)

        # Filter out newlines and find identifiers
        identifiers = [t for t in tokens if t.type == "IDENTIFIER"]

        # Check line numbers increment
        assert identifiers[0].lineno < identifiers[1].lineno < identifiers[2].lineno


class TestRealWorldExample:
    """Test tokenization of real-world Quickshift code."""

    def test_complete_pipeline(self):
        """Test tokenizing a complete pipeline."""
        code = """
        # Simple pipeline example
        source: Source(parquet) = Source(path="s3://bucket/data/*.parquet")
        sink: Sink(csv) = Sink(path="file://output/")

        source_test: Test = Test(
            target=source,
            checks=[not_null("id"), unique("id")]
        )

        source.select("id", "name").where("age" > 18)
        source >> sink
        """

        tokens = tokenize_string(code)

        # Verify we got tokens
        assert len(tokens) > 0

        # Verify key components exist
        assert any(t.type == "SOURCE" for t in tokens)
        assert any(t.type == "SINK" for t in tokens)
        assert any(t.type == "TEST" for t in tokens)
        assert any(t.type == "PIPELINE" for t in tokens)
        assert any(t.type == "SELECT" for t in tokens)
        assert any(t.type == "WHERE" for t in tokens)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
