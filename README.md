# Quickshift

**A high-performance, Python-based Domain-Specific Language for local file-structure data manipulation**

Quickshift is a functional DSL designed to simplify and accelerate file-based data operations on any machine. It
combines Python-like syntax with DAG-style task orchestration, lazy evaluation, and LLVM-powered native code compilation
to deliver fast, intuitive data transformations.

## Overview

Quickshift provides a declarative, source-to-sink approach to data manipulation, enabling users to read data in any
format, apply transformations, and write output in any format—all with integrated validation and transformation
capabilities. The language is built on four core pillars:

**Functional Programming Model**: Immutable data operations with method chaining for readable, composable
transformations.

**Lazy Evaluation**: Operations are defined but not executed until explicitly triggered (via `.show` or task execution),
enabling query optimization and efficient resource usage.

**Native Performance**: A Python-based lexer and parser compile Quickshift syntax via LLVM to fast native machine code,
eliminating interpreter overhead.

**Test-First Philosophy**: Inspired by Go's built-in testing conventions, Quickshift requires test definitions alongside
task declarations to ensure data quality and structural integrity before execution.

## Core Architecture

### Language Components

Quickshift consists of five primary architectural layers:

**Lexer**: Tokenizes Quickshift source code into meaningful units (keywords, operators, identifiers).

**Parser**: Constructs an Abstract Syntax Tree (AST) from tokens, validating syntax and building the logical execution
plan.

**Test Validator**: Executes pre-flight data quality and schema validation tests before task execution, preventing
corrupted data from propagating.

**Optimizer**: Analyzes the AST to reorder, reduce, or eliminate operations before execution (enabled by lazy
evaluation).

**LLVM Backend**: Compiles the optimized AST to native machine code for maximum performance.

### Source-to-Sink Pattern

Quickshift adopts the source-to-sink data pipeline pattern, where:

**Sources** represent input data (files, remote storage, in-memory datasets) with optional schema definitions.

**Transformations** are method-chained operations (select, filter, join, aggregate, partition) applied to sources.

**Tests** are mandatory validations that execute before tasks commence, ensuring data quality and schema
compliance.

**Sinks** represent output destinations (files, databases, cloud storage) with format conversion handled automatically.

The `>>` operator connects sources to sinks and triggers test validation before execution.

### Lazy Evaluation Strategy

Quickshift delays computation until results are required:

- Defining a source or transformation **does not** execute any operations.
- Operations accumulate in a computational graph (thunks) awaiting execution.
- Execution triggers when:
    - A sink operation completes (`source >> sink`), preceded by test validation
    - An explicit readout is requested (`.show`, `.schema`)
    - A task is invoked

This approach enables the optimizer to:

- Eliminate redundant operations (e.g., selecting columns that are immediately filtered out)
- Reorder operations for performance (e.g., push filters closer to sources)
- Minimize memory footprint by processing data in streaming fashion

### Test-First Execution Model

Following Go's testing philosophy, Quickshift enforces test definitions for all task operations:

**Co-location**: Test definitions exist alongside task definitions in the same file (similar to Go's `_test.go`
convention).[24][1]

**Automatic Execution**: Tests run automatically before task execution when using the `>>` operator.

**Failure Behavior**: If tests fail, the task aborts and returns detailed validation errors.

**Test Types**: Schema validation, data quality checks, completeness verification, and custom assertions.

## Syntax Design

### Type Annotations

Quickshift uses Python-inspired type annotations with format specifiers:

```
variable_name: Type(format) = Expression
```

**Type**: Core types include `Source`, `Sink`, `Task`, `Test`, `string`, `int`, `float`, `bool`
**format**: Optional file format specification for Sources/Sinks (`csv`, `parquet`, `json`, `avro`, etc.)

### Schema Definitions

Sources can declare schemas for validation:

```
schema={"column_name": type [constraint], ...}
```

**Constraints**: `not null`, `unique`, `> value`, `< value`, `in [values]`, `matches pattern`

### Test Definitions

Tests are declared using the `Test` type and associated with tasks:

```
test_name: Test = Test(
    target=source_or_sink,
    checks=[
        check_type(parameters),
        ...
    ]
)
```

Tests execute automatically before task execution when the task uses the `>>` operator.

### Path Patterns

File paths support:

- **Local files**: `file://path/to/files/*.csv`
- **Cloud storage**: `s3://`, `gs://`, `wasbs://` with wildcard patterns
- **In-memory**: `data=[{...}, {...}]` for inline datasets

### Method Chaining

Transformation methods chain fluently:

```
source.select(...).where(...).partition(...).cast(...)
```

Methods return modified source references, enabling continued chaining. All transformations are lazy.

### The Pipeline Operator (`>>`)

The `>>` operator creates data flows with automatic test execution:

```
source >> sink  # Runs associated tests before execution
```

This operator:

- Executes all tests associated with the source or sink
- Marks the end of transformation definitions
- Triggers compilation and optimization if tests pass
- Returns a `Task` object when assigned, enabling task composition
- Aborts with detailed errors if tests fail

### Task Composition

Tasks can be chained to form DAG-like execution plans:

```
task1: Task = source1 >> sink1  # Tests run before task1 executes
task2: Task = source2 >> sink2  # Tests run before task2 executes
task1 >> task2  # task2 executes after task1 completes successfully
```

## Testing Framework

### Philosophy

Quickshift adopts Go's test-first approach where tests are mandatory, co-located with code, and automatically executed.
This ensures:

**Early Detection**: Data quality issues are caught before propagation.

**Documentation**: Tests serve as living documentation of expected data behavior.

**Confidence**: Teams can refactor and extend pipelines knowing tests will catch regressions.

**CI/CD Integration**: Tests integrate seamlessly into deployment pipelines.

### Test Types

Quickshift provides built-in test primitives for common data quality checks:

#### Schema Validation Tests

```
schema_check(): Validates that data conforms to declared schema
column_exists("col_name"): Ensures specified columns are present
column_type("col_name", type): Validates column data types
```

#### Completeness Tests

```
not_null("col_name"): Ensures no null values in specified column
not_empty(): Validates dataset contains at least one row
required_columns([col_names]): Ensures all required columns exist
```

#### Accuracy Tests

```
value_range("col_name", min, max): Validates values fall within range
value_in("col_name", [values]): Ensures values are from allowed set
matches_pattern("col_name", regex): Validates string patterns
```

#### Consistency Tests

```
unique("col_name"): Ensures all values are unique
referential_integrity(source_col, target_source, target_col): Validates foreign key relationships
cross_field_validation("col1" < "col2"): Ensures logical relationships between fields
```

#### Anomaly Detection Tests

```
outlier_detection("col_name", threshold): Flags statistical outliers
volume_check(min_rows, max_rows): Validates expected data volume
freshness_check(max_age): Ensures data is not stale
```

#### Custom Tests

```
custom(lambda row: expression): User-defined validation logic
```

### Test Declaration Syntax

Tests are declared using the `Test` type and must target a source or sink:

```
my_test: Test = Test(
    target=my_source,
    checks=[
        schema_check(),
        not_null("user_id"),
        value_range("age", 0, 120),
        unique("email"),
        volume_check(min_rows=1)
    ],
    on_fail="abort"  # Options: "abort", "warn", "log"
)
```

**target**: The Source or Sink to validate
**checks**: List of validation checks to execute
**on_fail**: Behavior when tests fail (default: "abort")

### Test Execution

Tests execute automatically in the following scenarios:

**Implicit Execution**: When using the `>>` operator, all tests targeting the source or sink execute before data
transfer.

```
my_source: Source(csv) = Source(path="file://data/*.csv")
my_sink: Sink(parquet) = Sink(path="file://output/")

my_test: Test = Test(
    target=my_source,
    checks=[not_null("id"), schema_check()]
)

# Tests execute automatically before data flows
my_source >> my_sink  # my_test runs first
```

**Explicit Execution**: Tests can be manually triggered for debugging:

```
my_test.run()  # Returns test results without executing the task
```

**Batch Execution**: Multiple tests can be grouped:

```
test_suite: Test = Test(
    target=my_source,
    checks=[
        not_null("id"),
        unique("email"),
        value_range("created_at", "2020-01-01", "2025-12-31")
    ]
)
```

### Test Results

Test execution returns structured results:

```
{
    "status": "passed" | "failed" | "warning",
    "total_checks": 5,
    "passed": 4,
    "failed": 1,
    "warnings": 0,
    "failures": [
        {
            "check": "not_null",
            "column": "email",
            "message": "Found 3 null values in column 'email'",
            "affected_rows": [10, 25, 47]
        }
    ]
}
```

Failed tests prevent task execution and log detailed error information.

### Test File Convention

Following Go's `_test.go` pattern, Quickshift test files use the `_test.qs` suffix:

```
pipeline.qs         # Main pipeline definition
pipeline_test.qs    # Test definitions for pipeline.qs
```

Tests in `_test.qs` files automatically associate with tasks in the corresponding `.qs` file.

### Advanced Testing Patterns

#### Pre and Post-Transformation Tests

```
source: Source(csv) = Source(path="file://raw/*.csv")
sink: Sink(parquet) = Sink(path="file://processed/")

# Test source data quality
source_test: Test = Test(
    target=source,
    checks=[not_null("id"), unique("id"), schema_check()]
)

# Apply transformations
source.select("id", "name", "amount").where("amount" > 0)

# Test transformed data before writing
transform_test: Test = Test(
    target=source,
    checks=[
        not_null("amount"),
        value_range("amount", 0.01, 1000000),
        custom(lambda row: row["amount"] > 0)
    ]
)

# Both tests execute before sink writes
source >> sink
```

#### Conditional Testing

```
my_test: Test = Test(
    target=my_source,
    checks=[
        not_null("id"),
        conditional(
            when="environment" == "production",
            then=[unique("email"), referential_integrity("user_id", users, "id")]
        )
    ]
)
```

#### Sampling for Performance

```
large_test: Test = Test(
    target=large_source,
    checks=[value_range("score", 0, 100)],
    sample_size=10000  # Test only 10k rows for performance
)
```

#### Cross-Source Validation

```
users: Source(parquet) = Source(path="file://users/*.parquet")
orders: Source(parquet) = Source(path="file://orders/*.parquet")

# Validate referential integrity between sources
integrity_test: Test = Test(
    target=orders,
    checks=[referential_integrity("user_id", users, "id")]
)

orders >> processed_sink  # Test ensures all orders have valid users
```

## Language Features

### Data Sources

**File-based sources** with automatic format detection:

```
source: Source(csv) = Source(path="file://data/*.csv")
```

**Remote sources** with authentication:

```
source: Source(avro) = Source(path="gs://bucket/data/*.avro")
```

**In-memory sources** for testing or small datasets:

```
source: Source() = Source(
    data=[{"col1": "val1", "col2": 123}],
    schema={"col1": string not null, "col2": int}
)
```

### Transformations

**Selection and projection**:

```
source.select("col1", "col2" as "renamed_col", cast("col3" to string) as "col3_str")
```

**Filtering**:

```
source.where("col1" == "value")
source.where("col1" > 10 and "col2" in ["a", "b"])
```

**Joins**:

```
source1.join(source2, "join_key1", "join_key2", type="inner")  # Types: inner, left, right, full
```

**Aggregations**:

```
source.agg("column", "count")
source.agg("amount", "sum")
source.group_by("category").agg("revenue", "avg")
```

**Partitioning**:

```
source.partition("col1", "col2")
```

**Data manipulation** (for in-memory sources):

```
source.insert(row={"col1": "new_val"})
source.drop("column_name")
source.drop(row=0)
source.rename("old_col", "new_col")
```

### Data Sinks

**File-based sinks** with format conversion:

```
sink: Sink(parquet) = Sink(path="file://output/")
```

**Cloud sinks**:

```
sink: Sink(avro) = Sink(path="s3://bucket/output/")
```

**Future capabilities** (database and warehouse sinks):

```
sink: Sink(BigQuery) = Sink(
    table="table_name",
    project="project_id",
    dataset="dataset_name",
    credentials="path/to/creds.json"
)
```

### Control Flow

**Loops** for dynamic pipeline generation:

```
values: string = ["val1", "val2", "val3"]
for item in values:
    source: Source(csv) = Source(path="data/" + item + "/*.csv")
    source >> sink
```

**Conditionals**:

```
if environment == "production":
    sink: Sink(parquet) = Sink(path="s3://prod-bucket/output/")
else:
    sink: Sink(parquet) = Sink(path="file://local/output/")
```

### Execution and Debugging

**Immediate execution**:

```
task.show  # Displays results (bypasses tests for debugging)
task.schema  # Shows schema information
```

**Test execution**:

```
my_test.run()  # Execute test without running task
my_test.report()  # Display test results summary
```

Without `.show` or `.schema`, tasks remain unevaluated until their results are required.

## Example Workflows

### Simple Format Conversion with Testing

```
source: Source(csv) = Source(
    path="file://input/*.csv",
    schema={"id": int not null, "name": string not null, "amount": float}
)
sink: Sink(parquet) = Sink(path="file://output/")

# Define validation tests
validation: Test = Test(
    target=source,
    checks=[
        schema_check(),
        not_null("id"),
        unique("id"),
        value_range("amount", 0, 1000000),
        volume_check(min_rows=1)
    ]
)

# Tests execute automatically before conversion
source >> sink
```

### Multi-Stage Pipeline with Comprehensive Testing

```
raw_source: Source(json) = Source(path="s3://raw-data/*.json")
processed_sink: Sink(parquet) = Sink(path="s3://processed-data/")

# Test raw data quality
raw_tests: Test = Test(
    target=raw_source,
    checks=[
        not_null("user_id"),
        not_null("timestamp"),
        matches_pattern("email", "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"),
        freshness_check(max_age="24h")
    ]
)

# Apply transformations
raw_source
    .select("user_id", "email", "purchase_amount", "timestamp")
    .where("purchase_amount" > 0)
    .cast("timestamp" to datetime)

# Test transformed data
processed_tests: Test = Test(
    target=raw_source,
    checks=[
        value_range("purchase_amount", 0.01, 100000),
        not_empty(),
        cross_field_validation("timestamp" < now())
    ]
)

# Both test suites run before sink writes
raw_source >> processed_sink
```

### Dynamic Pipeline with Loop-Level Testing

```
categories: string = ["electronics", "books", "clothing"]
sink: Sink(parquet) = Sink(path="s3://warehouse/aggregated/")

for category in categories:
    source: Source(csv) = Source(path="s3://raw/" + category + "/*.csv")
    
    # Category-specific tests
    category_test: Test = Test(
        target=source,
        checks=[
            not_null("product_id"),
            not_null("price"),
            value_range("price", 0.01, 50000),
            unique("product_id"),
            volume_check(min_rows=10)  # Ensure meaningful data
        ]
    )
    
    source.select("product_id", "price", "sales").where("region" == "US")
    task: Task = source >> sink  # Tests run per iteration
    task
```

### In-Memory Testing and Development

```
test_data: Source() = Source(
    data=[
        {"user_id": 1, "email": "user1@test.com", "age": 25},
        {"user_id": 2, "email": "user2@test.com", "age": 30},
        {"user_id": 3, "email": "user3@test.com", "age": 35}
    ],
    schema={"user_id": int not null, "email": string not null, "age": int}
)

# Test in-memory data
mem_test: Test = Test(
    target=test_data,
    checks=[
        unique("user_id"),
        matches_pattern("email", "^.+@.+\\..+$"),
        value_range("age", 18, 100)
    ]
)

test_data.insert(row={"user_id": 4, "email": "user4@test.com", "age": 28})
test_data.show  # Bypasses tests for debugging
```

### Cross-Source Referential Integrity

```
users: Source(parquet) = Source(path="file://users/*.parquet")
orders: Source(parquet) = Source(path="file://orders/*.parquet")
output: Sink(parquet) = Sink(path="file://joined/")

# Validate users data
user_test: Test = Test(
    target=users,
    checks=[
        unique("user_id"),
        not_null("user_id"),
        not_null("email")
    ]
)

# Validate orders reference valid users
order_test: Test = Test(
    target=orders,
    checks=[
        not_null("order_id"),
        referential_integrity("user_id", users, "user_id"),
        value_range("order_total", 0.01, 1000000)
    ]
)

users.join(orders, "user_id", "user_id")
users >> output  # Both test suites execute before join
```

## Implementation Roadmap

### Phase 1: Core Language (First Iteration)

**Objective**: Build a working lexer, parser, and interpreter without LLVM compilation.

1. **Define tokens**: Keywords (`Source`, `Sink`, `Task`, `Test`, `where`, `select`, etc.), operators (`>>`, `==`,
   `as`), literals, identifiers.[20][18]

2. **Implement lexer** using Python PLY (lex.py module):
    - Tokenize Quickshift source files
    - Handle whitespace, comments
    - Report lexical errors with line numbers

3. **Implement parser** using PLY (yacc.py module):
    - Define grammar rules for variable declarations, method calls, operators, test definitions
    - Build Abstract Syntax Tree (AST)
    - Validate syntax and report parse errors

4. **Build testing framework**:
    - Implement built-in test primitives (schema_check, not_null, unique, etc.)
    - Create test execution engine
    - Integrate test validation into `>>` operator
    - Generate structured test results and error reports

5. **Build interpreter**:
    - Walk the AST and execute operations using Python libraries (pandas, pyarrow, etc.)
    - Implement lazy evaluation with deferred execution graphs
    - Support basic file I/O (CSV, JSON, Parquet via pandas/pyarrow)
    - Execute tests before task operations

6. **Test basic workflows**:
    - Simple source-to-sink conversions with validation
    - Select, filter, partition operations
    - In-memory data manipulation with tests
    - Test failure and error reporting

### Phase 2: Optimization and Extended Features

**Objective**: Add query optimization, extended transformations, and cloud storage support.

1. **Optimizer implementation**:
    - Analyze AST to detect redundant operations
    - Reorder transformations (predicate pushdown, projection pruning)
    - Optimize test execution (merge compatible checks, minimize data scans)
    - Generate optimized execution plans

2. **Extended operations**:
    - Join implementations (hash join, merge join)
    - Aggregations and group-by operations
    - Complex expressions and custom functions
    - Window functions and ranking operations

3. **Advanced testing features**:
    - Sampling strategies for large datasets
    - Statistical anomaly detection
    - Time-series freshness checks
    - Custom test function support
    - Test result persistence and reporting

4. **Cloud storage integration**:
    - S3, GCS, Azure Blob Storage connectors
    - Authentication and credential management
    - Streaming reads/writes for large datasets
    - Remote test execution optimization

5. **Task DAG execution**:
    - Task dependency resolution
    - Parallel task execution where possible
    - Error handling and rollback strategies
    - Test result aggregation across DAG

### Phase 3: LLVM Compilation

**Objective**: Replace the Python interpreter with LLVM-compiled native code.

1. **AST to LLVM IR translation**:
    - Map Quickshift AST nodes to LLVM intermediate representation
    - Implement type system and memory management
    - Handle data structure layouts and operations
    - Compile test predicates to native code

2. **LLVM optimization passes**:
    - Apply LLVM's built-in optimizations
    - Custom optimization passes for data operations
    - Test predicate optimization and vectorization

3. **Code generation**:
    - Compile LLVM IR to native machine code
    - Link with runtime libraries for I/O operations
    - Generate standalone executables or JIT-compiled code
    - Native test execution engine

4. **Performance benchmarking**:
    - Compare interpreted vs. compiled execution
    - Optimize hot paths identified through profiling
    - Benchmark test overhead and optimize

### Phase 4: Ecosystem and Tooling

**Objective**: Build developer tools and extend integrations.

1. **Language Server Protocol (LSP)** for IDE support:
    - Syntax highlighting
    - Autocompletion for test primitives
    - Error checking and inline diagnostics
    - Test coverage visualization

2. **Testing framework enhancements**:
    - Test result dashboards
    - Historical test tracking
    - Test coverage metrics
    - Integration with Great Expectations and other tools
    - CI/CD pipeline integration

3. **Database and warehouse sinks**:
    - PostgreSQL, MySQL, SQLite support
    - BigQuery, Snowflake, Redshift connectors
    - Streaming insert capabilities
    - Database-level constraint validation

4. **Documentation and examples**:
    - Comprehensive API reference
    - Tutorial notebooks and example workflows
    - Test pattern library and best practices
    - Performance tuning guides

## Design Principles

**Simplicity**: Python-like syntax minimizes the learning curve for data engineers familiar with Python.

**Test-First**: Mandatory testing ensures data quality and serves as living documentation.

**Composability**: Method chaining and task composition enable building complex workflows from simple operations.

**Performance**: LLVM compilation delivers near-native speed without sacrificing expressiveness.

**Flexibility**: Format-agnostic sources and sinks support diverse data ecosystems.

**Safety**: Schema validation, constraint checking, and automated testing prevent runtime errors.

**Scalability**: Syntax designed to handle both simple file operations and complex multi-stage DAGs.

## Technical Dependencies

**Core**:

- Python 3.9+ (host language for lexer/parser development)
- PLY (Python Lex-Yacc) for lexical analysis and parsing
- LLVM 14+ for native code compilation

**Data Processing** (initial interpreter):

- pandas (CSV, Excel, JSON)
- pyarrow (Parquet, Arrow formats)
- fsspec (cloud storage abstraction)

**Testing Framework**:

- pytest (test runner integration)
- hypothesis (property-based testing)
- Great Expectations (advanced validation rules)

**Cloud Integration**:

- boto3 (AWS S3)
- google-cloud-storage (GCS)
- azure-storage-blob (Azure)

**Future**:

- Database drivers (psycopg2, pymysql, etc.)
- Warehouse SDKs (google-cloud-bigquery, snowflake-connector-python)
- dbt integration for transformation testing

## Getting Started

### Installation (Future)

```bash
pip install quickshift
```

### Running Quickshift

```bash
quickshift pipeline.qs        # Execute pipeline
quickshift test pipeline.qs   # Run tests only
quickshift --no-test pipeline.qs  # Skip tests (not recommended)
```

Or using the Python API:

```python
from quickshift import compile_and_run, run_tests

# Run tests and execute
compile_and_run("pipeline.qs")

# Run tests only
results = run_tests("pipeline.qs")
print(results)
```

## Best Practices

### Test Coverage

**Always define tests** for production pipelines, covering:

- Schema compliance at source
- Data quality post-transformation
- Volume and freshness checks
- Cross-source referential integrity

### Test Granularity

**Balance performance and coverage**:

- Use sampling for large datasets (millions of rows)
- Apply full validation to critical columns
- Reserve expensive checks (regex, cross-joins) for samples

### Failure Handling

**Configure appropriate failure modes**:

- `abort`: Stop execution on failure (default, recommended for production)
- `warn`: Log warnings but continue (for non-critical checks)
- `log`: Record issues without alerts (for monitoring)

### Test Maintenance

**Keep tests synchronized with code**:

- Update tests when schemas change
- Remove obsolete checks
- Document why tests exist (business logic context)
- Version control test thresholds

### CI/CD Integration

**Embed tests in deployment pipelines**:

- Run test-only mode in pre-deployment validation
- Maintain test result history
- Alert on test degradation trends
- Require test pass before production deployment

## Contributing

Quickshift is in active development. Contributions are welcome for:

- Language feature proposals
- Test primitive implementations
- Performance optimizations
- Connector implementations
- Documentation and examples
- Test pattern library expansion

## License

[To be determined]
