"""
Unit tests for the Semantic Analyzer
"""

import unittest
from quickshift.lexer import Lexer
from quickshift.parser import Parser
from quickshift.semantic_analyzer import SemanticAnalyzer, SemanticError


class TestSemanticAnalyzer(unittest.TestCase):
    
    def analyze(self, source):
        """Helper to analyze source code"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        analyzer = SemanticAnalyzer()
        return analyzer.analyze(ast)
    
    def test_variable_declaration_with_type(self):
        # Should not raise any error
        self.analyze("let x: int = 5;")
    
    def test_type_inference(self):
        # Should infer int type
        self.analyze("let x = 42;")
    
    def test_type_mismatch(self):
        with self.assertRaises(SemanticError):
            self.analyze("let x: int = 3.14;")
    
    def test_undefined_variable(self):
        with self.assertRaises(SemanticError):
            self.analyze("x = 10;")
    
    def test_const_assignment(self):
        with self.assertRaises(SemanticError):
            self.analyze("const x: int = 5; x = 10;")
    
    def test_function_declaration(self):
        self.analyze("function add(a: int, b: int) -> int { return a + b; }")
    
    def test_function_call(self):
        self.analyze("""
            function add(a: int, b: int) -> int { return a + b; }
            let x = add(5, 10);
        """)
    
    def test_function_call_wrong_args(self):
        with self.assertRaises(SemanticError):
            self.analyze("""
                function add(a: int, b: int) -> int { return a + b; }
                let x = add(5);
            """)
    
    def test_function_call_wrong_type(self):
        with self.assertRaises(SemanticError):
            self.analyze("""
                function add(a: int, b: int) -> int { return a + b; }
                let x = add(3.14, 5);
            """)
    
    def test_return_type_mismatch(self):
        with self.assertRaises(SemanticError):
            self.analyze("""
                function get_number() -> int { return 3.14; }
            """)
    
    def test_return_outside_function(self):
        with self.assertRaises(SemanticError):
            self.analyze("return 42;")
    
    def test_if_condition_not_bool(self):
        with self.assertRaises(SemanticError):
            self.analyze("if (5) { }")
    
    def test_while_condition_not_bool(self):
        with self.assertRaises(SemanticError):
            self.analyze("while (10) { }")
    
    def test_binary_op_int(self):
        self.analyze("let x = 5 + 10;")
    
    def test_binary_op_float(self):
        self.analyze("let x = 3.14 * 2.0;")
    
    def test_binary_op_mixed(self):
        # int + float should be allowed (result is float)
        self.analyze("let x: float = 5 + 3.14;")
    
    def test_comparison(self):
        self.analyze("let x = 5 < 10;")
    
    def test_logical_and(self):
        self.analyze("let x = true and false;")
    
    def test_logical_or(self):
        self.analyze("let x = true or false;")
    
    def test_unary_minus(self):
        self.analyze("let x = -5;")
    
    def test_unary_not(self):
        self.analyze("let x = not true;")
    
    def test_scope(self):
        # Variables in inner scope should not be visible in outer scope
        self.analyze("""
            let x = 5;
            if (true) {
                let y = 10;
            }
        """)
    
    def test_redeclaration_error(self):
        with self.assertRaises(SemanticError):
            self.analyze("""
                let x = 5;
                let x = 10;
            """)


if __name__ == '__main__':
    unittest.main()
