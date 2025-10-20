"""
Reserved keywords for the Quickshift DSL.
"""

# Reserved keywords mapping lowercase to token names
RESERVED = {
    # Core types
    "Source": "SOURCE",
    "Sink": "SINK",
    "Task": "TASK",
    "Test": "TEST",
    # Data types
    "string": "STRING_TYPE",
    "int": "INT_TYPE",
    "float": "FLOAT_TYPE",
    "bool": "BOOL_TYPE",
    "datetime": "DATETIME_TYPE",
    # File formats ToDo: More will be added
    "csv": "CSV",
    "parquet": "PARQUET",
    "json": "JSON",
    "avro": "AVRO",
    "postgres": "POSTGRES",
    "BigQuery": "BIGQUERY",
    # Control flow
    "for": "FOR",
    "in": "IN",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    # Logical operators
    "and": "AND",
    "or": "OR",
    "not": "NOT",
    # Schema constraints
    "null": "NULL",
    # Methods/Functions
    "select": "SELECT",
    "where": "WHERE",
    "join": "JOIN",
    "partition": "PARTITION",
    "cast": "CAST",
    "to": "TO",
    "as": "AS",
    "agg": "AGG",
    "group_by": "GROUP_BY",
    "insert": "INSERT",
    "drop": "DROP",
    "rename": "RENAME",
    "add_column": "ADD_COLUMN",
    "show": "SHOW",
    "schema": "SCHEMA",
    "anti_join": "ANTI_JOIN",
    # Test check functions
    "schema_check": "SCHEMA_CHECK",
    "not_null": "NOT_NULL",
    "unique": "UNIQUE",
    "value_range": "VALUE_RANGE",
    "value_in": "VALUE_IN",
    "matches_pattern": "MATCHES_PATTERN",
    "referential_integrity": "REFERENTIAL_INTEGRITY",
    "cross_field_validation": "CROSS_FIELD_VALIDATION",
    "outlier_detection": "OUTLIER_DETECTION",
    "volume_check": "VOLUME_CHECK",
    "freshness_check": "FRESHNESS_CHECK",
    "custom": "CUSTOM",
    "conditional": "CONDITIONAL",
    # Test configuration
    "target": "TARGET",
    "checks": "CHECKS",
    "on_fail": "ON_FAIL",
    "when": "WHEN",
    "then": "THEN",
    "sample_size": "SAMPLE_SIZE",
    # Source/Sink configuration
    "path": "PATH",
    "data": "DATA",
    "connection": "CONNECTION",
    "table": "TABLE",
    "project": "PROJECT",
    "dataset": "DATASET",
    "credentials": "CREDENTIALS",
    "write_disposition": "WRITE_DISPOSITION",
    "create_disposition": "CREATE_DISPOSITION",
    # Join types
    "inner": "INNER",
    "left": "LEFT",
    "right": "RIGHT",
    "full": "FULL",
    "type": "TYPE",
    # Built-in functions
    "now": "NOW",
    "generate_uuid": "GENERATE_UUID",
    "len": "LEN",
    "lambda": "LAMBDA",
    "row": "ROW",
    # Event handlers
    "on_success": "ON_SUCCESS",
    "on_failure": "ON_FAILURE",
    "log": "LOG",
    "alert": "ALERT",
    # Other
    "environment": "ENVIRONMENT",
    "min_rows": "MIN_ROWS",
    "max_rows": "MAX_ROWS",
    "max_age": "MAX_AGE",
}

# Generate list of reserved keyword values for token list
RESERVED_TOKENS = list(RESERVED.values())
