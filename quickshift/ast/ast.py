class ASTNode:
    pass


class Assignment(ASTNode):
    def __init__(self, var_name, expression):
        self.var_name = var_name
        self.expression = expression

    def __repr__(self):
        return f"Assignment({self.var_name} = {self.expression})"


class SourceCall(ASTNode):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def __repr__(self):
        return f"SourceCall({self.kwargs})"


class SchemaCall(ASTNode):
    def __init__(self, columns):
        self.columns = columns

    def __repr__(self):
        return f"SchemaCall({self.columns})"


class ColumnCall(ASTNode):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def __repr__(self):
        return f"ColumnCall({self.kwargs})"


class SelectStatement(ASTNode):
    def __init__(self, columns, source):
        self.columns = columns
        self.source = source

    def __repr__(self):
        return f"SelectStatement(columns={self.columns}, source={self.source})"
