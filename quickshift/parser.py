"""
Parser for the Quickshift DSL
Builds an Abstract Syntax Tree from tokens
"""

from typing import List, Optional
from .token_types import Token, TokenType
from .ast_nodes import (
    Program, Statement, Expression, IntegerLiteral, FloatLiteral,
    StringLiteral, BooleanLiteral, Identifier, VariableDeclaration,
    Assignment, BinaryOp, UnaryOp, IfStatement, WhileStatement,
    ForStatement, Parameter, FunctionDeclaration, FunctionCall,
    ReturnStatement, Block, ExpressionStatement
)


class ParserError(Exception):
    """Exception raised for parsing errors"""
    pass


class Parser:
    """
    Recursive descent parser for Quickshift DSL
    Builds an AST from a stream of tokens
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
    
    def current_token(self) -> Token:
        """Get the current token"""
        if self.position >= len(self.tokens):
            return self.tokens[-1]  # Return EOF
        return self.tokens[self.position]
    
    def peek(self, offset: int = 1) -> Token:
        """Peek ahead at the next token(s)"""
        pos = self.position + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]  # Return EOF
        return self.tokens[pos]
    
    def advance(self) -> Token:
        """Move to the next token"""
        token = self.current_token()
        if self.position < len(self.tokens) - 1:
            self.position += 1
        return token
    
    def expect(self, token_type: TokenType) -> Token:
        """Expect a specific token type and advance"""
        token = self.current_token()
        if token.type != token_type:
            raise ParserError(f"Expected {token_type}, got {token.type} at {token.line}:{token.column}")
        return self.advance()
    
    def skip_newlines(self):
        """Skip newline tokens"""
        while self.current_token().type == TokenType.NEWLINE:
            self.advance()
    
    def parse(self) -> Program:
        """Parse the entire program"""
        statements = []
        
        while self.current_token().type != TokenType.EOF:
            self.skip_newlines()
            if self.current_token().type == TokenType.EOF:
                break
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        return Program(statements)
    
    def parse_statement(self) -> Optional[Statement]:
        """Parse a statement"""
        self.skip_newlines()
        
        token_type = self.current_token().type
        
        # Variable declarations
        if token_type in (TokenType.LET, TokenType.CONST):
            return self.parse_variable_declaration()
        
        # Function declaration
        elif token_type == TokenType.FUNCTION:
            return self.parse_function_declaration()
        
        # Control flow
        elif token_type == TokenType.IF:
            return self.parse_if_statement()
        
        elif token_type == TokenType.WHILE:
            return self.parse_while_statement()
        
        elif token_type == TokenType.FOR:
            return self.parse_for_statement()
        
        elif token_type == TokenType.RETURN:
            return self.parse_return_statement()
        
        # Block
        elif token_type == TokenType.LBRACE:
            return self.parse_block()
        
        # Assignment or expression statement
        else:
            # Check if it's an assignment
            if self.current_token().type == TokenType.IDENTIFIER and self.peek().type == TokenType.ASSIGN:
                return self.parse_assignment()
            else:
                # Expression statement
                expr = self.parse_expression()
                if self.current_token().type == TokenType.SEMICOLON:
                    self.advance()
                return ExpressionStatement(expr)
    
    def parse_variable_declaration(self) -> VariableDeclaration:
        """Parse a variable declaration"""
        is_const = self.current_token().type == TokenType.CONST
        self.advance()  # Skip 'let' or 'const'
        
        name = self.expect(TokenType.IDENTIFIER).value
        
        type_name = None
        if self.current_token().type == TokenType.COLON:
            self.advance()
            type_name = self.parse_type()
        
        value = None
        if self.current_token().type == TokenType.ASSIGN:
            self.advance()
            value = self.parse_expression()
        
        if self.current_token().type == TokenType.SEMICOLON:
            self.advance()
        
        return VariableDeclaration(name, type_name, value, is_const)
    
    def parse_type(self) -> str:
        """Parse a type name"""
        token = self.current_token()
        if token.type in (TokenType.INT, TokenType.FLOAT_TYPE, TokenType.STRING_TYPE, 
                         TokenType.BOOL, TokenType.VOID):
            self.advance()
            return token.value
        else:
            raise ParserError(f"Expected type, got {token.type} at {token.line}:{token.column}")
    
    def parse_assignment(self) -> Assignment:
        """Parse an assignment statement"""
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        
        if self.current_token().type == TokenType.SEMICOLON:
            self.advance()
        
        return Assignment(name, value)
    
    def parse_function_declaration(self) -> FunctionDeclaration:
        """Parse a function declaration"""
        self.expect(TokenType.FUNCTION)
        name = self.expect(TokenType.IDENTIFIER).value
        
        self.expect(TokenType.LPAREN)
        parameters = []
        
        if self.current_token().type != TokenType.RPAREN:
            parameters = self.parse_parameter_list()
        
        self.expect(TokenType.RPAREN)
        
        return_type = "void"
        if self.current_token().type == TokenType.ARROW:
            self.advance()
            return_type = self.parse_type()
        
        body = []
        if self.current_token().type == TokenType.LBRACE:
            block = self.parse_block()
            body = block.statements
        
        return FunctionDeclaration(name, parameters, return_type, body)
    
    def parse_parameter_list(self) -> List[Parameter]:
        """Parse function parameters"""
        parameters = []
        
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.COLON)
        type_name = self.parse_type()
        parameters.append(Parameter(name, type_name))
        
        while self.current_token().type == TokenType.COMMA:
            self.advance()
            name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.COLON)
            type_name = self.parse_type()
            parameters.append(Parameter(name, type_name))
        
        return parameters
    
    def parse_if_statement(self) -> IfStatement:
        """Parse an if statement"""
        self.expect(TokenType.IF)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        
        then_block = []
        if self.current_token().type == TokenType.LBRACE:
            block = self.parse_block()
            then_block = block.statements
        else:
            stmt = self.parse_statement()
            if stmt:
                then_block = [stmt]
        
        else_block = None
        if self.current_token().type == TokenType.ELSE:
            self.advance()
            if self.current_token().type == TokenType.LBRACE:
                block = self.parse_block()
                else_block = block.statements
            else:
                stmt = self.parse_statement()
                if stmt:
                    else_block = [stmt]
        
        return IfStatement(condition, then_block, else_block)
    
    def parse_while_statement(self) -> WhileStatement:
        """Parse a while statement"""
        self.expect(TokenType.WHILE)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        
        body = []
        if self.current_token().type == TokenType.LBRACE:
            block = self.parse_block()
            body = block.statements
        else:
            stmt = self.parse_statement()
            if stmt:
                body = [stmt]
        
        return WhileStatement(condition, body)
    
    def parse_for_statement(self) -> ForStatement:
        """Parse a for statement"""
        self.expect(TokenType.FOR)
        self.expect(TokenType.LPAREN)
        
        # Init
        init = None
        if self.current_token().type != TokenType.SEMICOLON:
            init = self.parse_statement()
        else:
            self.advance()
        
        # Condition
        condition = None
        if self.current_token().type != TokenType.SEMICOLON:
            condition = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        
        # Increment
        increment = None
        if self.current_token().type != TokenType.RPAREN:
            if self.current_token().type == TokenType.IDENTIFIER and self.peek().type == TokenType.ASSIGN:
                increment = self.parse_assignment()
            else:
                expr = self.parse_expression()
                increment = ExpressionStatement(expr)
        
        self.expect(TokenType.RPAREN)
        
        body = []
        if self.current_token().type == TokenType.LBRACE:
            block = self.parse_block()
            body = block.statements
        else:
            stmt = self.parse_statement()
            if stmt:
                body = [stmt]
        
        return ForStatement(init, condition, increment, body)
    
    def parse_return_statement(self) -> ReturnStatement:
        """Parse a return statement"""
        self.expect(TokenType.RETURN)
        
        value = None
        if self.current_token().type not in (TokenType.SEMICOLON, TokenType.NEWLINE, TokenType.EOF):
            value = self.parse_expression()
        
        if self.current_token().type == TokenType.SEMICOLON:
            self.advance()
        
        return ReturnStatement(value)
    
    def parse_block(self) -> Block:
        """Parse a block of statements"""
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        statements = []
        while self.current_token().type != TokenType.RBRACE and self.current_token().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        return Block(statements)
    
    def parse_expression(self) -> Expression:
        """Parse an expression"""
        return self.parse_logical_or()
    
    def parse_logical_or(self) -> Expression:
        """Parse logical OR expression"""
        left = self.parse_logical_and()
        
        while self.current_token().type == TokenType.OR:
            op = self.advance().value
            right = self.parse_logical_and()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_logical_and(self) -> Expression:
        """Parse logical AND expression"""
        left = self.parse_equality()
        
        while self.current_token().type == TokenType.AND:
            op = self.advance().value
            right = self.parse_equality()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_equality(self) -> Expression:
        """Parse equality expression"""
        left = self.parse_comparison()
        
        while self.current_token().type in (TokenType.EQUAL, TokenType.NOT_EQUAL):
            op = self.advance().value
            right = self.parse_comparison()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_comparison(self) -> Expression:
        """Parse comparison expression"""
        left = self.parse_additive()
        
        while self.current_token().type in (TokenType.LESS_THAN, TokenType.LESS_EQUAL, 
                                           TokenType.GREATER_THAN, TokenType.GREATER_EQUAL):
            op = self.advance().value
            right = self.parse_additive()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_additive(self) -> Expression:
        """Parse additive expression"""
        left = self.parse_multiplicative()
        
        while self.current_token().type in (TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.parse_multiplicative()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_multiplicative(self) -> Expression:
        """Parse multiplicative expression"""
        left = self.parse_unary()
        
        while self.current_token().type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op = self.advance().value
            right = self.parse_unary()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_unary(self) -> Expression:
        """Parse unary expression"""
        if self.current_token().type in (TokenType.MINUS, TokenType.NOT):
            op = self.advance().value
            operand = self.parse_unary()
            return UnaryOp(op, operand)
        
        return self.parse_primary()
    
    def parse_primary(self) -> Expression:
        """Parse primary expression"""
        token = self.current_token()
        
        # Literals
        if token.type == TokenType.INTEGER:
            self.advance()
            return IntegerLiteral(token.value)
        
        elif token.type == TokenType.FLOAT:
            self.advance()
            return FloatLiteral(token.value)
        
        elif token.type == TokenType.STRING:
            self.advance()
            return StringLiteral(token.value)
        
        elif token.type == TokenType.BOOLEAN:
            self.advance()
            return BooleanLiteral(token.value)
        
        # Identifier or function call
        elif token.type == TokenType.IDENTIFIER:
            name = self.advance().value
            
            # Function call
            if self.current_token().type == TokenType.LPAREN:
                self.advance()
                arguments = []
                
                if self.current_token().type != TokenType.RPAREN:
                    arguments.append(self.parse_expression())
                    
                    while self.current_token().type == TokenType.COMMA:
                        self.advance()
                        arguments.append(self.parse_expression())
                
                self.expect(TokenType.RPAREN)
                return FunctionCall(name, arguments)
            
            # Just an identifier
            else:
                return Identifier(name)
        
        # Parenthesized expression
        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        else:
            raise ParserError(f"Unexpected token {token.type} at {token.line}:{token.column}")
