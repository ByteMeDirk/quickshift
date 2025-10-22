"""
Compiler that translates Quickshift AST into executable Python code.
"""

from quickshift.ast.ast import *


class QuickshiftCompiler:
    """Compiles Quickshift AST into Python/Pandas code."""

    def __init__(self):
        self.generated_code = []
        self.imports = set()

    def compile(self, ast):
        self._add_imports()
        for node in ast:
            if isinstance(node, Assignment):
                self._compile_assignment(node)
            elif isinstance(node, SelectStatement):
                self._compile_select(node)
        return self._get_code()

    def _compile_select(self, node):
        """Compile SELECT ... FROM ... into Python."""
        source = node.source
        cols = node.columns

        if cols == '*':
            code = f"print({source})"
        else:
            # Convert col1, col2 → ['col1', 'col2']
            cols_list = ', '.join([f'\"{c}\"' for c in cols])
            code = f"print({source}[[{cols_list}]])"

        self.generated_code.append(code)

    def _add_imports(self):
        """Add necessary Python imports."""
        self.imports.add("import pandas as pd")
        self.imports.add("import sqlalchemy")
        self.imports.add("from pathlib import Path")


    def _compile_assignment(self, node):
        """Compile an assignment statement."""
        var_name = node.var_name
        expression = self._compile_expression(node.expression)
        self.generated_code.append(f"{var_name} = {expression}")

    def _compile_expression(self, node):
        """Compile an expression node."""
        if isinstance(node, SourceCall):
            return self._compile_source_call(node)
        return str(node)

    def _compile_source_call(self, node):
        """Compile a source() call into appropriate pandas read function."""
        kwargs = node.kwargs
        source_type = kwargs.get('type', 'csv')
        path = kwargs.get('path', '')

        if source_type == 'csv':
            return self._compile_csv_source(kwargs)
        elif source_type == 'parquet':
            return self._compile_parquet_source(kwargs)
        elif source_type == 'postgres':
            return self._compile_postgres_source(kwargs)
        else:
            raise ValueError(f"Unknown source type: {source_type}")

    def _compile_csv_source(self, kwargs):
        """Compile CSV source into pd.read_csv()."""
        path = kwargs.get('path', '')
        schema = kwargs.get('schema')

        code = f"pd.read_csv('{path}'"

        if schema:
            dtype_dict = self._compile_schema_to_dtype(schema)
            code += f", dtype={dtype_dict}"

        code += ")"
        return code

    def _compile_parquet_source(self, kwargs):
        """Compile Parquet source into pd.read_parquet()."""
        path = kwargs.get('path', '')
        schema = kwargs.get('schema')

        code = f"pd.read_parquet('{path}'"

        if schema:
            dtype_dict = self._compile_schema_to_dtype(schema)
            code += f", dtype={dtype_dict}"

        code += ")"
        return code

    def _compile_postgres_source(self, kwargs):
        """Compile Postgres source into pd.read_sql()."""
        path = kwargs.get('path', '')
        table = kwargs.get('table', '')

        code = f"pd.read_sql_table('{table}', con='{path}')"
        return code

    def _compile_schema_to_dtype(self, schema_node):
        """Convert SchemaCall to pandas dtype dictionary."""
        if not isinstance(schema_node, SchemaCall):
            return {}

        dtype_map = {
            'str': 'str',
            'int': 'Int64',  # Nullable integer
            'float': 'Float64',
            'bool': 'boolean'
        }

        dtype_dict = {}
        for column in schema_node.columns:
            if isinstance(column, ColumnCall):
                col_name = column.kwargs.get('name')
                col_type = column.kwargs.get('type')
                nullable = column.kwargs.get('nullable', True)

                if col_name and col_type:
                    # Map DSL types to pandas types
                    pandas_type = dtype_map.get(col_type, 'object')
                    dtype_dict[col_name] = pandas_type

        return dtype_dict

    def _get_code(self):
        """Return the complete generated Python code."""
        imports = '\n'.join(sorted(self.imports))
        code = '\n'.join(self.generated_code)
        return f"{imports}\n\n{code}"


def compile_and_execute(ast):
    """Compile AST and execute the generated Python code."""
    compiler = QuickshiftCompiler()
    python_code = compiler.compile(ast)

    print("Generated Python Code:")
    print("=" * 60)
    print(python_code)
    print("=" * 60)

    # Execute the code
    exec_globals = {}
    exec(python_code, exec_globals)

    # Return variables created during execution
    return {k: v for k, v in exec_globals.items()
            if not k.startswith('_') and k not in ['pd', 'sqlalchemy', 'Path']}
