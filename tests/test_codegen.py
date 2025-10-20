"""
Unit tests for the Code Generator
"""

import unittest
from quickshift.lexer import Lexer
from quickshift.parser import Parser
from quickshift.semantic_analyzer import SemanticAnalyzer
from quickshift.codegen import CodeGenerator


class TestCodeGenerator(unittest.TestCase):
    
    def compile(self, source):
        """Helper to compile source code to LLVM IR"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        codegen = CodeGenerator()
        return codegen.generate(ast)
    
    def test_function_declaration(self):
        ir = self.compile("function test() -> void { }")
        self.assertIn("define void", ir)
        self.assertIn("test", ir)
    
    def test_function_with_params(self):
        ir = self.compile("function add(a: int, b: int) -> int { return a + b; }")
        self.assertIn("define i32", ir)
        self.assertIn("add", ir)
        self.assertIn("i32", ir)
    
    def test_return_statement(self):
        ir = self.compile("function get_five() -> int { return 5; }")
        self.assertIn("ret i32", ir)
    
    def test_variable_declaration(self):
        ir = self.compile("""
            function test() -> int {
                let x: int = 42;
                return x;
            }
        """)
        self.assertIn("alloca i32", ir)
        self.assertIn("store", ir)
        self.assertIn("load", ir)
    
    def test_binary_operations(self):
        ir = self.compile("""
            function test() -> int {
                let x: int = 5 + 3;
                return x;
            }
        """)
        self.assertIn("add", ir)
    
    def test_comparison(self):
        ir = self.compile("""
            function test() -> bool {
                let x: bool = 5 < 10;
                return x;
            }
        """)
        self.assertIn("icmp", ir)
    
    def test_if_statement(self):
        ir = self.compile("""
            function test(x: int) -> int {
                if (x > 0) {
                    return 1;
                } else {
                    return -1;
                }
            }
        """)
        self.assertIn("br i1", ir)
        self.assertIn("if.then", ir)
        self.assertIn("if.else", ir)
    
    def test_while_loop(self):
        ir = self.compile("""
            function test() -> int {
                let i: int = 0;
                while (i < 10) {
                    i = i + 1;
                }
                return i;
            }
        """)
        self.assertIn("while.cond", ir)
        self.assertIn("while.body", ir)
    
    def test_for_loop(self):
        ir = self.compile("""
            function test() -> int {
                let sum: int = 0;
                for (let i: int = 0; i < 10; i = i + 1) {
                    sum = sum + i;
                }
                return sum;
            }
        """)
        self.assertIn("for.cond", ir)
        self.assertIn("for.body", ir)
        self.assertIn("for.inc", ir)
    
    def test_function_call(self):
        ir = self.compile("""
            function add(a: int, b: int) -> int {
                return a + b;
            }
            function test() -> int {
                let x: int = add(5, 3);
                return x;
            }
        """)
        self.assertIn("call i32", ir)
        self.assertIn("add", ir)
    
    def test_float_operations(self):
        ir = self.compile("""
            function test() -> float {
                let x: float = 3.14 + 2.71;
                return x;
            }
        """)
        self.assertIn("fadd", ir)


if __name__ == '__main__':
    unittest.main()
