"""
Main entry point for Quickshift DSL.
"""

from quickshift.parser.parser import QuickshiftParser
from quickshift.compiler.compiler import QuickshiftCompiler, compile_and_execute


def main():
    code = """
my_data = source(type=csv, path='data.csv');
select age from my_data;
"""

    # Parse
    parser = QuickshiftParser()
    ast = parser.parse(code)

    print("Parsed AST:")
    print("=" * 60)
    for node in ast:
        print(f"  {node}")
    print()

    # Compile and execute

    compile_and_execute(ast)



if __name__ == '__main__':
    main()
