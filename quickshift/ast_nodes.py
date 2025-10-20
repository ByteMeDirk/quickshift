"""
Abstract Syntax Tree (AST) node definitions for the Quickshift DSL
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any


class ASTNode(ABC):
    """Base class for all AST nodes"""
    
    @abstractmethod
    def __repr__(self):
        pass


class Program(ASTNode):
    """Root node representing the entire program"""
    
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements
    
    def __repr__(self):
        return f"Program({self.statements})"


class Statement(ASTNode):
    """Base class for statements"""
    pass


class Expression(ASTNode):
    """Base class for expressions"""
    pass


# Literals
class IntegerLiteral(Expression):
    def __init__(self, value: int):
        self.value = value
    
    def __repr__(self):
        return f"IntegerLiteral({self.value})"


class FloatLiteral(Expression):
    def __init__(self, value: float):
        self.value = value
    
    def __repr__(self):
        return f"FloatLiteral({self.value})"


class StringLiteral(Expression):
    def __init__(self, value: str):
        self.value = value
    
    def __repr__(self):
        return f"StringLiteral({self.value!r})"


class BooleanLiteral(Expression):
    def __init__(self, value: bool):
        self.value = value
    
    def __repr__(self):
        return f"BooleanLiteral({self.value})"


# Variables
class Identifier(Expression):
    def __init__(self, name: str):
        self.name = name
    
    def __repr__(self):
        return f"Identifier({self.name})"


class VariableDeclaration(Statement):
    def __init__(self, name: str, type_name: Optional[str], value: Optional[Expression], is_const: bool = False):
        self.name = name
        self.type_name = type_name
        self.value = value
        self.is_const = is_const
    
    def __repr__(self):
        return f"VariableDeclaration({self.name}, {self.type_name}, {self.value}, const={self.is_const})"


class Assignment(Statement):
    def __init__(self, name: str, value: Expression):
        self.name = name
        self.value = value
    
    def __repr__(self):
        return f"Assignment({self.name}, {self.value})"


# Binary operations
class BinaryOp(Expression):
    def __init__(self, left: Expression, operator: str, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right
    
    def __repr__(self):
        return f"BinaryOp({self.left}, {self.operator}, {self.right})"


# Unary operations
class UnaryOp(Expression):
    def __init__(self, operator: str, operand: Expression):
        self.operator = operator
        self.operand = operand
    
    def __repr__(self):
        return f"UnaryOp({self.operator}, {self.operand})"


# Control flow
class IfStatement(Statement):
    def __init__(self, condition: Expression, then_block: List[Statement], else_block: Optional[List[Statement]] = None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
    
    def __repr__(self):
        return f"IfStatement({self.condition}, {self.then_block}, {self.else_block})"


class WhileStatement(Statement):
    def __init__(self, condition: Expression, body: List[Statement]):
        self.condition = condition
        self.body = body
    
    def __repr__(self):
        return f"WhileStatement({self.condition}, {self.body})"


class ForStatement(Statement):
    def __init__(self, init: Optional[Statement], condition: Optional[Expression], 
                 increment: Optional[Statement], body: List[Statement]):
        self.init = init
        self.condition = condition
        self.increment = increment
        self.body = body
    
    def __repr__(self):
        return f"ForStatement({self.init}, {self.condition}, {self.increment}, {self.body})"


# Functions
class Parameter(ASTNode):
    def __init__(self, name: str, type_name: str):
        self.name = name
        self.type_name = type_name
    
    def __repr__(self):
        return f"Parameter({self.name}, {self.type_name})"


class FunctionDeclaration(Statement):
    def __init__(self, name: str, parameters: List[Parameter], return_type: str, body: List[Statement]):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body
    
    def __repr__(self):
        return f"FunctionDeclaration({self.name}, {self.parameters}, {self.return_type}, {self.body})"


class FunctionCall(Expression):
    def __init__(self, name: str, arguments: List[Expression]):
        self.name = name
        self.arguments = arguments
    
    def __repr__(self):
        return f"FunctionCall({self.name}, {self.arguments})"


class ReturnStatement(Statement):
    def __init__(self, value: Optional[Expression] = None):
        self.value = value
    
    def __repr__(self):
        return f"ReturnStatement({self.value})"


# Block
class Block(Statement):
    def __init__(self, statements: List[Statement]):
        self.statements = statements
    
    def __repr__(self):
        return f"Block({self.statements})"


# Expression statement (for expressions used as statements)
class ExpressionStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression
    
    def __repr__(self):
        return f"ExpressionStatement({self.expression})"
