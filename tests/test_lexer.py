"""
Unit tests for the Lexer
"""

import unittest
from quickshift.lexer import Lexer, LexerError
from quickshift.token_types import TokenType, Token


class TestLexer(unittest.TestCase):
    
    def test_integers(self):
        lexer = Lexer("42 123 0")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.INTEGER)
        self.assertEqual(tokens[0].value, 42)
        self.assertEqual(tokens[1].type, TokenType.INTEGER)
        self.assertEqual(tokens[1].value, 123)
    
    def test_floats(self):
        lexer = Lexer("3.14 0.5 42.0")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.FLOAT)
        self.assertEqual(tokens[0].value, 3.14)
        self.assertEqual(tokens[1].type, TokenType.FLOAT)
        self.assertEqual(tokens[1].value, 0.5)
    
    def test_strings(self):
        lexer = Lexer('"hello" "world"')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].value, "hello")
        self.assertEqual(tokens[1].type, TokenType.STRING)
        self.assertEqual(tokens[1].value, "world")
    
    def test_string_escapes(self):
        lexer = Lexer(r'"hello\nworld\t"')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].value, "hello\nworld\t")
    
    def test_keywords(self):
        lexer = Lexer("let const if else while for function return")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.LET)
        self.assertEqual(tokens[1].type, TokenType.CONST)
        self.assertEqual(tokens[2].type, TokenType.IF)
        self.assertEqual(tokens[3].type, TokenType.ELSE)
        self.assertEqual(tokens[4].type, TokenType.WHILE)
        self.assertEqual(tokens[5].type, TokenType.FOR)
        self.assertEqual(tokens[6].type, TokenType.FUNCTION)
        self.assertEqual(tokens[7].type, TokenType.RETURN)
    
    def test_identifiers(self):
        lexer = Lexer("x my_var hello123 _test")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].value, "x")
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].value, "my_var")
    
    def test_operators(self):
        lexer = Lexer("+ - * / % = == != < <= > >=")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.PLUS)
        self.assertEqual(tokens[1].type, TokenType.MINUS)
        self.assertEqual(tokens[2].type, TokenType.MULTIPLY)
        self.assertEqual(tokens[3].type, TokenType.DIVIDE)
        self.assertEqual(tokens[4].type, TokenType.MODULO)
        self.assertEqual(tokens[5].type, TokenType.ASSIGN)
        self.assertEqual(tokens[6].type, TokenType.EQUAL)
        self.assertEqual(tokens[7].type, TokenType.NOT_EQUAL)
        self.assertEqual(tokens[8].type, TokenType.LESS_THAN)
        self.assertEqual(tokens[9].type, TokenType.LESS_EQUAL)
        self.assertEqual(tokens[10].type, TokenType.GREATER_THAN)
        self.assertEqual(tokens[11].type, TokenType.GREATER_EQUAL)
    
    def test_delimiters(self):
        lexer = Lexer("( ) { } [ ] ; , : ->")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.LPAREN)
        self.assertEqual(tokens[1].type, TokenType.RPAREN)
        self.assertEqual(tokens[2].type, TokenType.LBRACE)
        self.assertEqual(tokens[3].type, TokenType.RBRACE)
        self.assertEqual(tokens[4].type, TokenType.LBRACKET)
        self.assertEqual(tokens[5].type, TokenType.RBRACKET)
        self.assertEqual(tokens[6].type, TokenType.SEMICOLON)
        self.assertEqual(tokens[7].type, TokenType.COMMA)
        self.assertEqual(tokens[8].type, TokenType.COLON)
        self.assertEqual(tokens[9].type, TokenType.ARROW)
    
    def test_comments(self):
        lexer = Lexer("let x = 5; // this is a comment\nlet y = 10;")
        tokens = lexer.tokenize()
        # Should skip the comment
        identifiers = [t for t in tokens if t.type == TokenType.IDENTIFIER]
        self.assertEqual(len(identifiers), 2)
    
    def test_multiline_comment(self):
        lexer = Lexer("let x = 5; /* this is a\nmultiline comment */ let y = 10;")
        tokens = lexer.tokenize()
        identifiers = [t for t in tokens if t.type == TokenType.IDENTIFIER]
        self.assertEqual(len(identifiers), 2)
    
    def test_booleans(self):
        lexer = Lexer("true false")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.BOOLEAN)
        self.assertEqual(tokens[0].value, True)
        self.assertEqual(tokens[1].type, TokenType.BOOLEAN)
        self.assertEqual(tokens[1].value, False)
    
    def test_invalid_character(self):
        lexer = Lexer("let x = @;")
        with self.assertRaises(LexerError):
            lexer.tokenize()


if __name__ == '__main__':
    unittest.main()
