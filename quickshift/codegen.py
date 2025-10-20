"""
LLVM IR Code Generator for the Quickshift DSL
Generates LLVM IR from the AST
"""

from typing import Dict, Optional
from llvmlite import ir
from .ast_nodes import (
    Program, Statement, Expression, IntegerLiteral, FloatLiteral,
    StringLiteral, BooleanLiteral, Identifier, VariableDeclaration,
    Assignment, BinaryOp, UnaryOp, IfStatement, WhileStatement,
    ForStatement, FunctionDeclaration, FunctionCall, ReturnStatement,
    Block, ExpressionStatement
)


class CodeGenError(Exception):
    """Exception raised for code generation errors"""
    pass


class CodeGenerator:
    """
    LLVM IR code generator for Quickshift DSL
    Converts AST to LLVM IR
    """
    
    def __init__(self):
        # Create the module and builder
        self.module = ir.Module(name="quickshift_module")
        self.builder: Optional[ir.IRBuilder] = None
        self.current_function = None
        
        # Symbol tables for tracking variables and functions
        self.variables: Dict[str, ir.Value] = {}
        self.functions: Dict[str, ir.Function] = {}
        
        # Type mapping
        self.type_map = {
            'int': ir.IntType(32),
            'float': ir.FloatType(),
            'bool': ir.IntType(1),
            'void': ir.VoidType(),
            'string': ir.IntType(8).as_pointer(),  # char*
        }
    
    def get_llvm_type(self, type_name: str) -> ir.Type:
        """Get LLVM type from type name"""
        if type_name not in self.type_map:
            raise CodeGenError(f"Unknown type: {type_name}")
        return self.type_map[type_name]
    
    def generate(self, ast: Program) -> str:
        """Generate LLVM IR from AST"""
        # Process all function declarations first
        for stmt in ast.statements:
            if isinstance(stmt, FunctionDeclaration):
                self.declare_function(stmt)
        
        # Then generate code for all statements
        for stmt in ast.statements:
            if isinstance(stmt, FunctionDeclaration):
                self.generate_statement(stmt)
            # Skip global variable declarations for now (they need special handling)
            elif isinstance(stmt, VariableDeclaration):
                # Global variables would need to be handled differently in LLVM
                # For now, we skip them or could implement as global constants
                pass
        
        return str(self.module)
    
    def declare_function(self, func: FunctionDeclaration):
        """Declare a function (signature only)"""
        # Get parameter types
        param_types = [self.get_llvm_type(param.type_name) for param in func.parameters]
        
        # Get return type
        return_type = self.get_llvm_type(func.return_type)
        
        # Create function type
        func_type = ir.FunctionType(return_type, param_types)
        
        # Create function
        llvm_func = ir.Function(self.module, func_type, name=func.name)
        
        # Name parameters
        for i, param in enumerate(func.parameters):
            llvm_func.args[i].name = param.name
        
        self.functions[func.name] = llvm_func
    
    def generate_statement(self, stmt: Statement):
        """Generate code for a statement"""
        if isinstance(stmt, VariableDeclaration):
            self.generate_variable_declaration(stmt)
        
        elif isinstance(stmt, Assignment):
            self.generate_assignment(stmt)
        
        elif isinstance(stmt, FunctionDeclaration):
            self.generate_function_declaration(stmt)
        
        elif isinstance(stmt, IfStatement):
            self.generate_if_statement(stmt)
        
        elif isinstance(stmt, WhileStatement):
            self.generate_while_statement(stmt)
        
        elif isinstance(stmt, ForStatement):
            self.generate_for_statement(stmt)
        
        elif isinstance(stmt, ReturnStatement):
            self.generate_return_statement(stmt)
        
        elif isinstance(stmt, Block):
            self.generate_block(stmt)
        
        elif isinstance(stmt, ExpressionStatement):
            self.generate_expression(stmt.expression)
    
    def generate_variable_declaration(self, decl: VariableDeclaration):
        """Generate code for a variable declaration"""
        if not self.builder:
            raise CodeGenError("Cannot declare variable outside function")
        
        # Get type
        var_type = self.get_llvm_type(decl.type_name)
        
        # Allocate space on stack
        var_ptr = self.builder.alloca(var_type, name=decl.name)
        
        # Initialize if value provided
        if decl.value:
            value = self.generate_expression(decl.value)
            # Cast if necessary
            if var_type != value.type:
                if isinstance(var_type, ir.FloatType) and isinstance(value.type, ir.IntType):
                    value = self.builder.sitofp(value, var_type)
            self.builder.store(value, var_ptr)
        
        self.variables[decl.name] = var_ptr
    
    def generate_assignment(self, assign: Assignment):
        """Generate code for an assignment"""
        if not self.builder:
            raise CodeGenError("Cannot assign outside function")
        
        # Get variable pointer
        if assign.name not in self.variables:
            raise CodeGenError(f"Undefined variable: {assign.name}")
        
        var_ptr = self.variables[assign.name]
        value = self.generate_expression(assign.value)
        
        # Cast if necessary
        target_type = var_ptr.type.pointee
        if target_type != value.type:
            if isinstance(target_type, ir.FloatType) and isinstance(value.type, ir.IntType):
                value = self.builder.sitofp(value, target_type)
        
        self.builder.store(value, var_ptr)
    
    def generate_function_declaration(self, func: FunctionDeclaration):
        """Generate code for a function declaration"""
        # Get the function
        llvm_func = self.functions[func.name]
        
        # Create entry block
        entry_block = llvm_func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(entry_block)
        
        # Save old function and variables
        old_function = self.current_function
        old_variables = self.variables.copy()
        self.current_function = llvm_func
        self.variables.clear()
        
        # Allocate space for parameters and store them
        for i, param in enumerate(func.parameters):
            param_type = self.get_llvm_type(param.type_name)
            param_ptr = self.builder.alloca(param_type, name=param.name)
            self.builder.store(llvm_func.args[i], param_ptr)
            self.variables[param.name] = param_ptr
        
        # Generate body
        for stmt in func.body:
            self.generate_statement(stmt)
        
        # Add return if not present
        if not self.builder.block.is_terminated:
            if func.return_type == 'void':
                self.builder.ret_void()
            else:
                # Return default value
                return_type = self.get_llvm_type(func.return_type)
                if isinstance(return_type, ir.IntType):
                    self.builder.ret(ir.Constant(return_type, 0))
                elif isinstance(return_type, ir.FloatType):
                    self.builder.ret(ir.Constant(return_type, 0.0))
        
        # Restore old function and variables
        self.current_function = old_function
        self.variables = old_variables
        self.builder = None
    
    def generate_if_statement(self, stmt: IfStatement):
        """Generate code for an if statement"""
        if not self.builder:
            raise CodeGenError("Cannot generate if statement outside function")
        
        # Evaluate condition
        condition = self.generate_expression(stmt.condition)
        
        # Create blocks
        then_block = self.current_function.append_basic_block(name="if.then")
        else_block = self.current_function.append_basic_block(name="if.else") if stmt.else_block else None
        merge_block = self.current_function.append_basic_block(name="if.merge")
        
        # Branch based on condition
        if else_block:
            self.builder.cbranch(condition, then_block, else_block)
        else:
            self.builder.cbranch(condition, then_block, merge_block)
        
        # Generate then block
        self.builder.position_at_end(then_block)
        for s in stmt.then_block:
            self.generate_statement(s)
        if not self.builder.block.is_terminated:
            self.builder.branch(merge_block)
        
        # Generate else block if present
        if else_block:
            self.builder.position_at_end(else_block)
            for s in stmt.else_block:
                self.generate_statement(s)
            if not self.builder.block.is_terminated:
                self.builder.branch(merge_block)
        
        # Continue at merge block
        self.builder.position_at_end(merge_block)
    
    def generate_while_statement(self, stmt: WhileStatement):
        """Generate code for a while statement"""
        if not self.builder:
            raise CodeGenError("Cannot generate while statement outside function")
        
        # Create blocks
        cond_block = self.current_function.append_basic_block(name="while.cond")
        body_block = self.current_function.append_basic_block(name="while.body")
        merge_block = self.current_function.append_basic_block(name="while.merge")
        
        # Jump to condition block
        self.builder.branch(cond_block)
        
        # Generate condition block
        self.builder.position_at_end(cond_block)
        condition = self.generate_expression(stmt.condition)
        self.builder.cbranch(condition, body_block, merge_block)
        
        # Generate body block
        self.builder.position_at_end(body_block)
        for s in stmt.body:
            self.generate_statement(s)
        if not self.builder.block.is_terminated:
            self.builder.branch(cond_block)
        
        # Continue at merge block
        self.builder.position_at_end(merge_block)
    
    def generate_for_statement(self, stmt: ForStatement):
        """Generate code for a for statement"""
        if not self.builder:
            raise CodeGenError("Cannot generate for statement outside function")
        
        # Generate init
        if stmt.init:
            self.generate_statement(stmt.init)
        
        # Create blocks
        cond_block = self.current_function.append_basic_block(name="for.cond")
        body_block = self.current_function.append_basic_block(name="for.body")
        inc_block = self.current_function.append_basic_block(name="for.inc")
        merge_block = self.current_function.append_basic_block(name="for.merge")
        
        # Jump to condition block
        self.builder.branch(cond_block)
        
        # Generate condition block
        self.builder.position_at_end(cond_block)
        if stmt.condition:
            condition = self.generate_expression(stmt.condition)
            self.builder.cbranch(condition, body_block, merge_block)
        else:
            self.builder.branch(body_block)
        
        # Generate body block
        self.builder.position_at_end(body_block)
        for s in stmt.body:
            self.generate_statement(s)
        if not self.builder.block.is_terminated:
            self.builder.branch(inc_block)
        
        # Generate increment block
        self.builder.position_at_end(inc_block)
        if stmt.increment:
            self.generate_statement(stmt.increment)
        self.builder.branch(cond_block)
        
        # Continue at merge block
        self.builder.position_at_end(merge_block)
    
    def generate_return_statement(self, stmt: ReturnStatement):
        """Generate code for a return statement"""
        if not self.builder:
            raise CodeGenError("Cannot generate return statement outside function")
        
        if stmt.value:
            value = self.generate_expression(stmt.value)
            self.builder.ret(value)
        else:
            self.builder.ret_void()
    
    def generate_block(self, block: Block):
        """Generate code for a block"""
        for stmt in block.statements:
            self.generate_statement(stmt)
    
    def generate_expression(self, expr: Expression) -> ir.Value:
        """Generate code for an expression"""
        if isinstance(expr, IntegerLiteral):
            return ir.Constant(ir.IntType(32), expr.value)
        
        elif isinstance(expr, FloatLiteral):
            return ir.Constant(ir.FloatType(), expr.value)
        
        elif isinstance(expr, BooleanLiteral):
            return ir.Constant(ir.IntType(1), int(expr.value))
        
        elif isinstance(expr, StringLiteral):
            # Create a global string constant
            # Note: For full implementation, strings should be stored as global constants
            # For now, we create a simple null-terminated string constant
            string_bytes = bytearray(expr.value.encode('utf-8') + b'\0')
            string_type = ir.ArrayType(ir.IntType(8), len(string_bytes))
            string_global = ir.GlobalVariable(self.module, string_type, 
                                             name=f".str.{len(self.module.globals)}")
            string_global.initializer = ir.Constant(string_type, string_bytes)
            string_global.global_constant = True
            # Return pointer to the string
            return self.builder.bitcast(string_global, ir.IntType(8).as_pointer())
        
        elif isinstance(expr, Identifier):
            if expr.name not in self.variables:
                # Check if it's a function parameter
                raise CodeGenError(f"Undefined variable: {expr.name}")
            var_ptr = self.variables[expr.name]
            return self.builder.load(var_ptr, name=expr.name)
        
        elif isinstance(expr, BinaryOp):
            return self.generate_binary_op(expr)
        
        elif isinstance(expr, UnaryOp):
            return self.generate_unary_op(expr)
        
        elif isinstance(expr, FunctionCall):
            return self.generate_function_call(expr)
        
        else:
            raise CodeGenError(f"Unknown expression type: {type(expr)}")
    
    def generate_binary_op(self, expr: BinaryOp) -> ir.Value:
        """Generate code for a binary operation"""
        left = self.generate_expression(expr.left)
        right = self.generate_expression(expr.right)
        
        # Promote int to float if needed
        if isinstance(left.type, ir.FloatType) and isinstance(right.type, ir.IntType):
            right = self.builder.sitofp(right, ir.FloatType())
        elif isinstance(right.type, ir.FloatType) and isinstance(left.type, ir.IntType):
            left = self.builder.sitofp(left, ir.FloatType())
        
        is_float = isinstance(left.type, ir.FloatType)
        
        # Arithmetic operators
        if expr.operator == '+':
            return self.builder.fadd(left, right) if is_float else self.builder.add(left, right)
        elif expr.operator == '-':
            return self.builder.fsub(left, right) if is_float else self.builder.sub(left, right)
        elif expr.operator == '*':
            return self.builder.fmul(left, right) if is_float else self.builder.mul(left, right)
        elif expr.operator == '/':
            return self.builder.fdiv(left, right) if is_float else self.builder.sdiv(left, right)
        elif expr.operator == '%':
            if is_float:
                return self.builder.frem(left, right)
            else:
                return self.builder.srem(left, right)
        
        # Comparison operators
        elif expr.operator == '<':
            return self.builder.fcmp_ordered('<', left, right) if is_float else self.builder.icmp_signed('<', left, right)
        elif expr.operator == '<=':
            return self.builder.fcmp_ordered('<=', left, right) if is_float else self.builder.icmp_signed('<=', left, right)
        elif expr.operator == '>':
            return self.builder.fcmp_ordered('>', left, right) if is_float else self.builder.icmp_signed('>', left, right)
        elif expr.operator == '>=':
            return self.builder.fcmp_ordered('>=', left, right) if is_float else self.builder.icmp_signed('>=', left, right)
        elif expr.operator == '==':
            return self.builder.fcmp_ordered('==', left, right) if is_float else self.builder.icmp_signed('==', left, right)
        elif expr.operator == '!=':
            return self.builder.fcmp_ordered('!=', left, right) if is_float else self.builder.icmp_signed('!=', left, right)
        
        # Logical operators
        elif expr.operator == 'and':
            return self.builder.and_(left, right)
        elif expr.operator == 'or':
            return self.builder.or_(left, right)
        
        else:
            raise CodeGenError(f"Unknown binary operator: {expr.operator}")
    
    def generate_unary_op(self, expr: UnaryOp) -> ir.Value:
        """Generate code for a unary operation"""
        operand = self.generate_expression(expr.operand)
        
        if expr.operator == '-':
            if isinstance(operand.type, ir.FloatType):
                return self.builder.fsub(ir.Constant(ir.FloatType(), 0.0), operand)
            else:
                return self.builder.sub(ir.Constant(operand.type, 0), operand)
        
        elif expr.operator == 'not':
            return self.builder.not_(operand)
        
        else:
            raise CodeGenError(f"Unknown unary operator: {expr.operator}")
    
    def generate_function_call(self, expr: FunctionCall) -> ir.Value:
        """Generate code for a function call"""
        if expr.name not in self.functions:
            raise CodeGenError(f"Undefined function: {expr.name}")
        
        func = self.functions[expr.name]
        
        # Generate arguments
        args = []
        for i, arg_expr in enumerate(expr.arguments):
            arg = self.generate_expression(arg_expr)
            # Cast if necessary
            expected_type = func.args[i].type
            if arg.type != expected_type:
                if isinstance(expected_type, ir.FloatType) and isinstance(arg.type, ir.IntType):
                    arg = self.builder.sitofp(arg, expected_type)
            args.append(arg)
        
        return self.builder.call(func, args)
