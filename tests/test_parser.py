"""
Unit tests for the Parser
"""

import unittest
from quickshift.lexer import Lexer
from quickshift.parser import Parser
from quickshift.ast_nodes import *


class TestParser(unittest.TestCase):
    
    def parse(self, source):
        """Helper to parse source code"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse()
    
    def test_variable_declaration(self):
        ast = self.parse("let x: int = 5;")
        self.assertEqual(len(ast.statements), 1)
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, VariableDeclaration)
        self.assertEqual(stmt.name, "x")
        self.assertEqual(stmt.type_name, "int")
        self.assertIsInstance(stmt.value, IntegerLiteral)
    
    def test_const_declaration(self):
        ast = self.parse("const PI: float = 3.14;")
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, VariableDeclaration)
        self.assertTrue(stmt.is_const)
    
    def test_type_inference(self):
        ast = self.parse("let x = 42;")
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, VariableDeclaration)
        self.assertIsNone(stmt.type_name)
    
    def test_assignment(self):
        ast = self.parse("x = 10;")
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, Assignment)
        self.assertEqual(stmt.name, "x")
    
    def test_function_declaration(self):
        ast = self.parse("function add(a: int, b: int) -> int { return a + b; }")
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, FunctionDeclaration)
        self.assertEqual(stmt.name, "add")
        self.assertEqual(len(stmt.parameters), 2)
        self.assertEqual(stmt.return_type, "int")
    
    def test_if_statement(self):
        ast = self.parse("if (x > 0) { let y = 1; }")
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, IfStatement)
        self.assertIsInstance(stmt.condition, BinaryOp)
        self.assertEqual(len(stmt.then_block), 1)
    
    def test_if_else_statement(self):
        ast = self.parse("if (x > 0) { let y = 1; } else { let y = -1; }")
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, IfStatement)
        self.assertIsNotNone(stmt.else_block)
        self.assertEqual(len(stmt.else_block), 1)
    
    def test_while_statement(self):
        ast = self.parse("while (x < 10) { x = x + 1; }")
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, WhileStatement)
        self.assertIsInstance(stmt.condition, BinaryOp)
    
    def test_for_statement(self):
        ast = self.parse("for (let i: int = 0; i < 10; i = i + 1) { }")
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, ForStatement)
        self.assertIsInstance(stmt.init, VariableDeclaration)
        self.assertIsInstance(stmt.condition, BinaryOp)
        self.assertIsInstance(stmt.increment, Assignment)
    
    def test_return_statement(self):
        ast = self.parse("return 42;")
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, ReturnStatement)
        self.assertIsInstance(stmt.value, IntegerLiteral)
    
    def test_function_call(self):
        ast = self.parse("let x = add(5, 10);")
        stmt = ast.statements[0]
        self.assertIsInstance(stmt.value, FunctionCall)
        self.assertEqual(stmt.value.name, "add")
        self.assertEqual(len(stmt.value.arguments), 2)
    
    def test_binary_operations(self):
        ast = self.parse("let x = 1 + 2 * 3;")
        stmt = ast.statements[0]
        # Should respect precedence: 1 + (2 * 3)
        self.assertIsInstance(stmt.value, BinaryOp)
        self.assertEqual(stmt.value.operator, '+')
        self.assertIsInstance(stmt.value.right, BinaryOp)
        self.assertEqual(stmt.value.right.operator, '*')
    
    def test_unary_operations(self):
        ast = self.parse("let x = -5;")
        stmt = ast.statements[0]
        self.assertIsInstance(stmt.value, UnaryOp)
        self.assertEqual(stmt.value.operator, '-')
    
    def test_comparison_operators(self):
        ast = self.parse("let x = a < b;")
        stmt = ast.statements[0]
        self.assertIsInstance(stmt.value, BinaryOp)
        self.assertEqual(stmt.value.operator, '<')
    
    def test_logical_operators(self):
        ast = self.parse("let x = true and false;")
        stmt = ast.statements[0]
        self.assertIsInstance(stmt.value, BinaryOp)
        self.assertEqual(stmt.value.operator, 'and')
    
    def test_parenthesized_expression(self):
        ast = self.parse("let x = (1 + 2) * 3;")
        stmt = ast.statements[0]
        # Should be: (1 + 2) * 3
        self.assertIsInstance(stmt.value, BinaryOp)
        self.assertEqual(stmt.value.operator, '*')
        self.assertIsInstance(stmt.value.left, BinaryOp)


if __name__ == '__main__':
    unittest.main()
