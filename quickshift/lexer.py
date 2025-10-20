"""
Lexer for the Quickshift DSL
Tokenizes input source code into tokens
"""

from typing import List, Optional
from .token_types import Token, TokenType


class LexerError(Exception):
    """Exception raised for lexical errors"""
    pass


class Lexer:
    """
    Lexical analyzer for Quickshift DSL
    Converts source code into a stream of tokens
    """
    
    KEYWORDS = {
        'let': TokenType.LET,
        'const': TokenType.CONST,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'for': TokenType.FOR,
        'function': TokenType.FUNCTION,
        'return': TokenType.RETURN,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
        'int': TokenType.INT,
        'float': TokenType.FLOAT_TYPE,
        'string': TokenType.STRING_TYPE,
        'bool': TokenType.BOOL,
        'void': TokenType.VOID,
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.NOT,
    }
    
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def current_char(self) -> Optional[str]:
        """Get the current character"""
        if self.position >= len(self.source):
            return None
        return self.source[self.position]
    
    def peek(self, offset: int = 1) -> Optional[str]:
        """Peek ahead at the next character(s)"""
        pos = self.position + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def advance(self) -> Optional[str]:
        """Move to the next character"""
        if self.position >= len(self.source):
            return None
        
        char = self.source[self.position]
        self.position += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return char
    
    def skip_whitespace(self):
        """Skip whitespace characters except newlines"""
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        """Skip single-line and multi-line comments"""
        if self.current_char() == '/' and self.peek() == '/':
            # Single-line comment
            while self.current_char() and self.current_char() != '\n':
                self.advance()
        elif self.current_char() == '/' and self.peek() == '*':
            # Multi-line comment
            self.advance()  # /
            self.advance()  # *
            while self.current_char():
                if self.current_char() == '*' and self.peek() == '/':
                    self.advance()  # *
                    self.advance()  # /
                    break
                self.advance()
    
    def read_number(self) -> Token:
        """Read a number (integer or float)"""
        start_line = self.line
        start_column = self.column
        num_str = ''
        is_float = False
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if is_float:
                    raise LexerError(f"Invalid number format at {self.line}:{self.column}")
                is_float = True
            num_str += self.current_char()
            self.advance()
        
        if is_float:
            return Token(TokenType.FLOAT, float(num_str), start_line, start_column)
        else:
            return Token(TokenType.INTEGER, int(num_str), start_line, start_column)
    
    def read_string(self) -> Token:
        """Read a string literal"""
        start_line = self.line
        start_column = self.column
        quote_char = self.current_char()
        self.advance()  # Skip opening quote
        
        string_value = ''
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()
                # Handle escape sequences
                escape_char = self.current_char()
                if escape_char == 'n':
                    string_value += '\n'
                elif escape_char == 't':
                    string_value += '\t'
                elif escape_char == 'r':
                    string_value += '\r'
                elif escape_char == '\\':
                    string_value += '\\'
                elif escape_char == quote_char:
                    string_value += quote_char
                else:
                    string_value += escape_char
                self.advance()
            else:
                string_value += self.current_char()
                self.advance()
        
        if not self.current_char():
            raise LexerError(f"Unterminated string at {start_line}:{start_column}")
        
        self.advance()  # Skip closing quote
        return Token(TokenType.STRING, string_value, start_line, start_column)
    
    def read_identifier(self) -> Token:
        """Read an identifier or keyword"""
        start_line = self.line
        start_column = self.column
        identifier = ''
        
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            identifier += self.current_char()
            self.advance()
        
        # Check if it's a keyword
        token_type = self.KEYWORDS.get(identifier, TokenType.IDENTIFIER)
        
        # Handle boolean literals
        if token_type == TokenType.TRUE:
            return Token(TokenType.BOOLEAN, True, start_line, start_column)
        elif token_type == TokenType.FALSE:
            return Token(TokenType.BOOLEAN, False, start_line, start_column)
        
        return Token(token_type, identifier, start_line, start_column)
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code"""
        while self.current_char():
            self.skip_whitespace()
            
            if not self.current_char():
                break
            
            # Comments
            if self.current_char() == '/' and (self.peek() == '/' or self.peek() == '*'):
                self.skip_comment()
                continue
            
            # Newlines
            if self.current_char() == '\n':
                line = self.line
                col = self.column
                self.advance()
                self.tokens.append(Token(TokenType.NEWLINE, '\n', line, col))
                continue
            
            # Numbers
            if self.current_char().isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Strings
            if self.current_char() in '"\'':
                self.tokens.append(self.read_string())
                continue
            
            # Identifiers and keywords
            if self.current_char().isalpha() or self.current_char() == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # Operators and delimiters
            line = self.line
            col = self.column
            char = self.current_char()
            
            if char == '+':
                self.tokens.append(Token(TokenType.PLUS, '+', line, col))
                self.advance()
            elif char == '-':
                if self.peek() == '>':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.ARROW, '->', line, col))
                else:
                    self.tokens.append(Token(TokenType.MINUS, '-', line, col))
                    self.advance()
            elif char == '*':
                self.tokens.append(Token(TokenType.MULTIPLY, '*', line, col))
                self.advance()
            elif char == '/':
                self.tokens.append(Token(TokenType.DIVIDE, '/', line, col))
                self.advance()
            elif char == '%':
                self.tokens.append(Token(TokenType.MODULO, '%', line, col))
                self.advance()
            elif char == '=':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.EQUAL, '==', line, col))
                else:
                    self.tokens.append(Token(TokenType.ASSIGN, '=', line, col))
                    self.advance()
            elif char == '!':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.NOT_EQUAL, '!=', line, col))
                else:
                    raise LexerError(f"Unexpected character '!' at {line}:{col}")
            elif char == '<':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.LESS_EQUAL, '<=', line, col))
                else:
                    self.tokens.append(Token(TokenType.LESS_THAN, '<', line, col))
                    self.advance()
            elif char == '>':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.GREATER_EQUAL, '>=', line, col))
                else:
                    self.tokens.append(Token(TokenType.GREATER_THAN, '>', line, col))
                    self.advance()
            elif char == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', line, col))
                self.advance()
            elif char == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', line, col))
                self.advance()
            elif char == '{':
                self.tokens.append(Token(TokenType.LBRACE, '{', line, col))
                self.advance()
            elif char == '}':
                self.tokens.append(Token(TokenType.RBRACE, '}', line, col))
                self.advance()
            elif char == '[':
                self.tokens.append(Token(TokenType.LBRACKET, '[', line, col))
                self.advance()
            elif char == ']':
                self.tokens.append(Token(TokenType.RBRACKET, ']', line, col))
                self.advance()
            elif char == ';':
                self.tokens.append(Token(TokenType.SEMICOLON, ';', line, col))
                self.advance()
            elif char == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', line, col))
                self.advance()
            elif char == ':':
                self.tokens.append(Token(TokenType.COLON, ':', line, col))
                self.advance()
            else:
                raise LexerError(f"Unexpected character '{char}' at {line}:{col}")
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
