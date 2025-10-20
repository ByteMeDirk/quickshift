"""
Semantic Analyzer for the Quickshift DSL
Performs type checking and semantic validation
"""

from typing import Dict, Optional, List
from .ast_nodes import *


class SemanticError(Exception):
    """Exception raised for semantic errors"""
    pass


class Symbol:
    """Represents a symbol in the symbol table"""
    
    def __init__(self, name: str, type_name: str, is_const: bool = False):
        self.name = name
        self.type_name = type_name
        self.is_const = is_const
    
    def __repr__(self):
        return f"Symbol({self.name}, {self.type_name}, const={self.is_const})"


class FunctionSymbol:
    """Represents a function in the symbol table"""
    
    def __init__(self, name: str, param_types: List[str], return_type: str):
        self.name = name
        self.param_types = param_types
        self.return_type = return_type
    
    def __repr__(self):
        return f"FunctionSymbol({self.name}, {self.param_types}, {self.return_type})"


class SymbolTable:
    """Symbol table for tracking variables and functions"""
    
    def __init__(self, parent: Optional['SymbolTable'] = None):
        self.symbols: Dict[str, Symbol] = {}
        self.functions: Dict[str, FunctionSymbol] = {}
        self.parent = parent
    
    def define(self, symbol: Symbol):
        """Define a new symbol"""
        if symbol.name in self.symbols:
            raise SemanticError(f"Variable '{symbol.name}' already defined in this scope")
        self.symbols[symbol.name] = symbol
    
    def define_function(self, func: FunctionSymbol):
        """Define a new function"""
        if func.name in self.functions:
            raise SemanticError(f"Function '{func.name}' already defined")
        self.functions[func.name] = func
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol"""
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.lookup(name)
        return None
    
    def lookup_function(self, name: str) -> Optional[FunctionSymbol]:
        """Look up a function"""
        if name in self.functions:
            return self.functions[name]
        elif self.parent:
            return self.parent.lookup_function(name)
        return None


class SemanticAnalyzer:
    """
    Semantic analyzer for Quickshift DSL
    Performs type checking and semantic validation
    """
    
    def __init__(self):
        self.global_scope = SymbolTable()
        self.current_scope = self.global_scope
        self.current_function = None
    
    def enter_scope(self):
        """Enter a new scope"""
        self.current_scope = SymbolTable(self.current_scope)
    
    def exit_scope(self):
        """Exit the current scope"""
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
    
    def analyze(self, ast: Program) -> Program:
        """Analyze the AST and return annotated AST"""
        for statement in ast.statements:
            self.analyze_statement(statement)
        return ast
    
    def analyze_statement(self, stmt: Statement):
        """Analyze a statement"""
        if isinstance(stmt, VariableDeclaration):
            self.analyze_variable_declaration(stmt)
        
        elif isinstance(stmt, Assignment):
            self.analyze_assignment(stmt)
        
        elif isinstance(stmt, FunctionDeclaration):
            self.analyze_function_declaration(stmt)
        
        elif isinstance(stmt, IfStatement):
            self.analyze_if_statement(stmt)
        
        elif isinstance(stmt, WhileStatement):
            self.analyze_while_statement(stmt)
        
        elif isinstance(stmt, ForStatement):
            self.analyze_for_statement(stmt)
        
        elif isinstance(stmt, ReturnStatement):
            self.analyze_return_statement(stmt)
        
        elif isinstance(stmt, Block):
            self.analyze_block(stmt)
        
        elif isinstance(stmt, ExpressionStatement):
            self.analyze_expression(stmt.expression)
    
    def analyze_variable_declaration(self, decl: VariableDeclaration):
        """Analyze a variable declaration"""
        # Analyze the value expression if present
        value_type = None
        if decl.value:
            value_type = self.analyze_expression(decl.value)
        
        # Infer type if not specified
        if decl.type_name is None:
            if value_type is None:
                raise SemanticError(f"Cannot infer type for variable '{decl.name}' without initializer")
            decl.type_name = value_type
        
        # Check type compatibility
        if value_type and decl.type_name != value_type:
            if not self.is_compatible(decl.type_name, value_type):
                raise SemanticError(
                    f"Type mismatch: cannot assign {value_type} to {decl.type_name} for variable '{decl.name}'"
                )
        
        # Define the symbol
        symbol = Symbol(decl.name, decl.type_name, decl.is_const)
        self.current_scope.define(symbol)
    
    def analyze_assignment(self, assign: Assignment):
        """Analyze an assignment"""
        # Look up the variable
        symbol = self.current_scope.lookup(assign.name)
        if not symbol:
            raise SemanticError(f"Undefined variable '{assign.name}'")
        
        # Check if it's const
        if symbol.is_const:
            raise SemanticError(f"Cannot assign to const variable '{assign.name}'")
        
        # Check type compatibility
        value_type = self.analyze_expression(assign.value)
        if not self.is_compatible(symbol.type_name, value_type):
            raise SemanticError(
                f"Type mismatch: cannot assign {value_type} to {symbol.type_name} for variable '{assign.name}'"
            )
    
    def analyze_function_declaration(self, func: FunctionDeclaration):
        """Analyze a function declaration"""
        # Get parameter types
        param_types = [param.type_name for param in func.parameters]
        
        # Define the function
        func_symbol = FunctionSymbol(func.name, param_types, func.return_type)
        self.current_scope.define_function(func_symbol)
        
        # Enter function scope
        old_function = self.current_function
        self.current_function = func_symbol
        self.enter_scope()
        
        # Define parameters
        for param in func.parameters:
            symbol = Symbol(param.name, param.type_name)
            self.current_scope.define(symbol)
        
        # Analyze body
        for stmt in func.body:
            self.analyze_statement(stmt)
        
        # Exit function scope
        self.exit_scope()
        self.current_function = old_function
    
    def analyze_if_statement(self, stmt: IfStatement):
        """Analyze an if statement"""
        # Check condition type
        cond_type = self.analyze_expression(stmt.condition)
        if cond_type != "bool":
            raise SemanticError(f"If condition must be boolean, got {cond_type}")
        
        # Analyze then block
        self.enter_scope()
        for s in stmt.then_block:
            self.analyze_statement(s)
        self.exit_scope()
        
        # Analyze else block if present
        if stmt.else_block:
            self.enter_scope()
            for s in stmt.else_block:
                self.analyze_statement(s)
            self.exit_scope()
    
    def analyze_while_statement(self, stmt: WhileStatement):
        """Analyze a while statement"""
        # Check condition type
        cond_type = self.analyze_expression(stmt.condition)
        if cond_type != "bool":
            raise SemanticError(f"While condition must be boolean, got {cond_type}")
        
        # Analyze body
        self.enter_scope()
        for s in stmt.body:
            self.analyze_statement(s)
        self.exit_scope()
    
    def analyze_for_statement(self, stmt: ForStatement):
        """Analyze a for statement"""
        self.enter_scope()
        
        # Analyze init
        if stmt.init:
            self.analyze_statement(stmt.init)
        
        # Check condition type
        if stmt.condition:
            cond_type = self.analyze_expression(stmt.condition)
            if cond_type != "bool":
                raise SemanticError(f"For condition must be boolean, got {cond_type}")
        
        # Analyze increment
        if stmt.increment:
            self.analyze_statement(stmt.increment)
        
        # Analyze body
        for s in stmt.body:
            self.analyze_statement(s)
        
        self.exit_scope()
    
    def analyze_return_statement(self, stmt: ReturnStatement):
        """Analyze a return statement"""
        if not self.current_function:
            raise SemanticError("Return statement outside function")
        
        if stmt.value:
            value_type = self.analyze_expression(stmt.value)
            if not self.is_compatible(self.current_function.return_type, value_type):
                raise SemanticError(
                    f"Return type mismatch: expected {self.current_function.return_type}, got {value_type}"
                )
        else:
            if self.current_function.return_type != "void":
                raise SemanticError(
                    f"Return type mismatch: expected {self.current_function.return_type}, got void"
                )
    
    def analyze_block(self, block: Block):
        """Analyze a block"""
        self.enter_scope()
        for stmt in block.statements:
            self.analyze_statement(stmt)
        self.exit_scope()
    
    def analyze_expression(self, expr: Expression) -> str:
        """Analyze an expression and return its type"""
        if isinstance(expr, IntegerLiteral):
            return "int"
        
        elif isinstance(expr, FloatLiteral):
            return "float"
        
        elif isinstance(expr, StringLiteral):
            return "string"
        
        elif isinstance(expr, BooleanLiteral):
            return "bool"
        
        elif isinstance(expr, Identifier):
            symbol = self.current_scope.lookup(expr.name)
            if not symbol:
                raise SemanticError(f"Undefined variable '{expr.name}'")
            return symbol.type_name
        
        elif isinstance(expr, BinaryOp):
            return self.analyze_binary_op(expr)
        
        elif isinstance(expr, UnaryOp):
            return self.analyze_unary_op(expr)
        
        elif isinstance(expr, FunctionCall):
            return self.analyze_function_call(expr)
        
        else:
            raise SemanticError(f"Unknown expression type: {type(expr)}")
    
    def analyze_binary_op(self, expr: BinaryOp) -> str:
        """Analyze a binary operation"""
        left_type = self.analyze_expression(expr.left)
        right_type = self.analyze_expression(expr.right)
        
        # Arithmetic operators
        if expr.operator in ['+', '-', '*', '/', '%']:
            if left_type in ['int', 'float'] and right_type in ['int', 'float']:
                # If either operand is float, result is float
                if left_type == 'float' or right_type == 'float':
                    return 'float'
                return 'int'
            else:
                raise SemanticError(
                    f"Invalid operands for {expr.operator}: {left_type} and {right_type}"
                )
        
        # Comparison operators
        elif expr.operator in ['<', '<=', '>', '>=']:
            if left_type in ['int', 'float'] and right_type in ['int', 'float']:
                return 'bool'
            else:
                raise SemanticError(
                    f"Invalid operands for {expr.operator}: {left_type} and {right_type}"
                )
        
        # Equality operators
        elif expr.operator in ['==', '!=']:
            if self.is_compatible(left_type, right_type) or self.is_compatible(right_type, left_type):
                return 'bool'
            else:
                raise SemanticError(
                    f"Invalid operands for {expr.operator}: {left_type} and {right_type}"
                )
        
        # Logical operators
        elif expr.operator in ['and', 'or']:
            if left_type == 'bool' and right_type == 'bool':
                return 'bool'
            else:
                raise SemanticError(
                    f"Invalid operands for {expr.operator}: {left_type} and {right_type}"
                )
        
        else:
            raise SemanticError(f"Unknown binary operator: {expr.operator}")
    
    def analyze_unary_op(self, expr: UnaryOp) -> str:
        """Analyze a unary operation"""
        operand_type = self.analyze_expression(expr.operand)
        
        if expr.operator == '-':
            if operand_type in ['int', 'float']:
                return operand_type
            else:
                raise SemanticError(f"Invalid operand for unary -: {operand_type}")
        
        elif expr.operator == 'not':
            if operand_type == 'bool':
                return 'bool'
            else:
                raise SemanticError(f"Invalid operand for unary not: {operand_type}")
        
        else:
            raise SemanticError(f"Unknown unary operator: {expr.operator}")
    
    def analyze_function_call(self, expr: FunctionCall) -> str:
        """Analyze a function call"""
        func = self.current_scope.lookup_function(expr.name)
        if not func:
            raise SemanticError(f"Undefined function '{expr.name}'")
        
        # Check argument count
        if len(expr.arguments) != len(func.param_types):
            raise SemanticError(
                f"Function '{expr.name}' expects {len(func.param_types)} arguments, got {len(expr.arguments)}"
            )
        
        # Check argument types
        for i, (arg, expected_type) in enumerate(zip(expr.arguments, func.param_types)):
            arg_type = self.analyze_expression(arg)
            if not self.is_compatible(expected_type, arg_type):
                raise SemanticError(
                    f"Argument {i+1} of function '{expr.name}': expected {expected_type}, got {arg_type}"
                )
        
        return func.return_type
    
    def is_compatible(self, target_type: str, source_type: str) -> bool:
        """Check if source_type can be assigned to target_type"""
        if target_type == source_type:
            return True
        
        # Allow int to float conversion
        if target_type == 'float' and source_type == 'int':
            return True
        
        return False
