"""
Main entry point for the Quickshift DSL compiler
"""

import sys
import argparse
from quickshift import Lexer, Parser, SemanticAnalyzer, CodeGenerator


def compile_file(filename: str, output_file: str = None, show_tokens: bool = False, 
                show_ast: bool = False, show_ir: bool = True):
    """Compile a Quickshift source file"""
    try:
        # Read source code
        with open(filename, 'r') as f:
            source = f.read()
        
        # Lexical analysis
        print(f"Compiling {filename}...")
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        if show_tokens:
            print("\n=== TOKENS ===")
            for token in tokens:
                if token.type.name != 'NEWLINE':
                    print(token)
        
        # Parsing
        parser = Parser(tokens)
        ast = parser.parse()
        
        if show_ast:
            print("\n=== AST ===")
            print(ast)
        
        # Semantic analysis
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        print("✓ Semantic analysis passed")
        
        # Code generation
        codegen = CodeGenerator()
        ir_code = codegen.generate(ast)
        
        if show_ir:
            print("\n=== LLVM IR ===")
            print(ir_code)
        
        # Write output
        if output_file:
            with open(output_file, 'w') as f:
                f.write(ir_code)
            print(f"\n✓ LLVM IR written to {output_file}")
        
        return True
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Quickshift DSL Compiler")
    parser.add_argument("input", help="Input source file")
    parser.add_argument("-o", "--output", help="Output LLVM IR file")
    parser.add_argument("-t", "--tokens", action="store_true", help="Show tokens")
    parser.add_argument("-a", "--ast", action="store_true", help="Show AST")
    parser.add_argument("--no-ir", action="store_true", help="Don't show LLVM IR")
    
    args = parser.parse_args()
    
    success = compile_file(
        args.input,
        args.output,
        show_tokens=args.tokens,
        show_ast=args.ast,
        show_ir=not args.no_ir
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
