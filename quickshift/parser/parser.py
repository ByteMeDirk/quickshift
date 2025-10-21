import ply.yacc as yacc

from quickshift.ast.ast import Assignment, SourceCall, SchemaCall, ColumnCall
from quickshift.lexer.lexer import QuickshiftLexer
from quickshift.utils.errors import QuickshiftParseError

lexer_instance = QuickshiftLexer()
tokens = QuickshiftLexer.tokens  # Required for yacc


class QuickshiftParser:
    """Parser for the Quickshift DSL."""

    def p_program(self, p):
        """
        program : statements
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
        statement : assignment NEWLINE
                  | NEWLINE
        """
        if len(p) == 3:
            p[0] = p[1]
        else:
            p[0] = None

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
        kwarg : IDENTIFIER EQUALS value
        """
        p[0] = {p[1]: p[3]}

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
        if p:
            raise QuickshiftParseError(
                f"Syntax error at line {p.lineno}, column {p.lexpos}, token '{p.value}'"
            )
        else:
            raise QuickshiftParseError("Syntax error at EOF")

    def __init__(self):
        self.lexer = lexer_instance.lexer
        self.parser = yacc.yacc(module=self)
