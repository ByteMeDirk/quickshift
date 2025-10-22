"""
Parser implementation for the Quickshift DSL using PLY.
"""

import ply.yacc as yacc

from quickshift.ast.ast import *
from quickshift.lexer.lexer import QuickshiftLexer
from quickshift.utils.errors import QuickshiftParseError


class QuickshiftParser:
    """Parser for the Quickshift DSL."""

    tokens = QuickshiftLexer.tokens  # Required by yacc

    def __init__(self):
        self.lexer = QuickshiftLexer()
        self.parser = yacc.yacc(module=self, debug=False)

    def parse(self, code):
        """Parse Quickshift code and return AST."""
        result = self.parser.parse(code, lexer=self.lexer.lexer)
        # Filter out None entries from empty lines
        return [node for node in result if node is not None]

    # ========================================================================
    # Grammar Rules
    # ========================================================================

    def p_program(self, p):
        """
        program : statement_list
        """
        p[0] = p[1]

    def p_statement_list(self, p):
        """
        statement_list : statement_list statement
                       | statement
        """
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_statement(self, p):
        """
        statement : assignment SEMICOLON
                  | select_statement SEMICOLON
                  | NEWLINE
        """
        if len(p) == 3:
            p[0] = p[1]
        else:
            p[0] = None

    def p_select_statement(self, p):
        """
        select_statement : SELECT select_targets FROM IDENTIFIER
        """
        p[0] = SelectStatement(p[2], p[4])

    def p_select_targets(self, p):
        """
        select_targets : select_list
                       | ASTERISK
        """
        p[0] = p[1]

    def p_select_list(self, p):
        """
        select_list : select_list COMMA IDENTIFIER
                    | IDENTIFIER
        """
        if len(p) == 4:
            # Extend existing list
            p[0] = p[1] + [p[3]]
        else:
            # Single column as base case
            p[0] = [p[1]]

    def p_assignment(self, p):
        """
        assignment : IDENTIFIER EQUALS source_call
        """
        p[0] = Assignment(p[1], p[3])

    def p_source_call(self, p):
        """
        source_call : SOURCE LPAREN kwargs RPAREN
        """
        p[0] = SourceCall(p[3])

    def p_schema_call(self, p):
        """
        schema_call : SCHEMA LPAREN column_list RPAREN
        """
        p[0] = SchemaCall(p[3])

    def p_column_call(self, p):
        """
        column_call : COLUMN LPAREN kwargs RPAREN
        """
        p[0] = ColumnCall(p[3])

    def p_column_list(self, p):
        """
        column_list : column_list COMMA column_call
                    | column_call
        """
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_kwargs(self, p):
        """
        kwargs : kwargs COMMA kwarg
               | kwarg
        """
        if len(p) == 4:
            p[1].update(p[3])
            p[0] = p[1]
        else:
            p[0] = p[1]

    def p_kwarg(self, p):
        """
        kwarg : kwarg_name EQUALS value
        """
        p[0] = {p[1]: p[3]}

    def p_kwarg_name(self, p):
        """
        kwarg_name : IDENTIFIER
                   | SCHEMA
                   | SOURCE
                   | COLUMN
        """
        # Convert token back to lowercase string for use as parameter name
        p[0] = p[1].lower() if isinstance(p[1], str) else p[1]

    def p_value(self, p):
        """
        value : STRING
              | NUMBER
              | TRUE
              | FALSE
              | IDENTIFIER
              | schema_call
        """
        if p[1] == "True":
            p[0] = True
        elif p[1] == "False":
            p[0] = False
        else:
            p[0] = p[1]

    def p_error(self, p):
        """Error handling rule."""
        if p:
            raise QuickshiftParseError(
                f"Syntax error at token '{p.value}'",
                line=p.lineno,
                token=p.value
            )
        else:
            raise QuickshiftParseError("Syntax error: unexpected end of file")
