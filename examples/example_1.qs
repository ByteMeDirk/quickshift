# example_1.qs
# Complex multi-source pipeline with conditional execution and comprehensive testing

# ============================================================================
# CONFIGURATION
# ============================================================================

# Environment settings
environment: string = "production"
project_id: string = "my-gcp-project"
dataset_name: string = "processed_data"

# ============================================================================
# SOURCE DEFINITIONS
# ============================================================================

# S3 Parquet Source - User transactions
s3_transactions: Source(parquet) = Source(
    path="s3://data-lake/transactions/*.parquet",
    schema={
        "transaction_id": string not null,
        "user_id": string not null,
        "amount": float not null,
        "category": string not null,
        "timestamp": datetime not null,
        "region": string
    }
)

# Second S3 Parquet Source - User profiles
s3_user_profiles: Source(parquet) = Source(
    path="s3://data-lake/user_profiles/*.parquet",
    schema={
        "user_id": string not null,
        "email": string not null,
        "account_type": string not null,
        "signup_date": datetime not null,
        "country": string not null
    }
)

# PostgreSQL Source - Filter criteria table
postgres_filters: Source(postgres) = Source(
    connection={
        "host": "postgres-prod.example.com",
        "port": 5432,
        "database": "analytics_db",
        "username": "etl_user",
        "password": "env:POSTGRES_PASSWORD",  # Read from environment variable
        "ssl_mode": "require"
    },
    table="active_user_filters",
    schema={
        "filter_id": int not null,
        "user_id": string not null,
        "filter_reason": string,
        "created_at": datetime not null
    }
)

# ============================================================================
# TEST DEFINITIONS - S3 Sources
# ============================================================================

# Test S3 transactions source
s3_transactions_test: Test = Test(
    target=s3_transactions,
    checks=[
        schema_check(),
        not_null("transaction_id"),
        not_null("user_id"),
        not_null("amount"),
        unique("transaction_id"),
        value_range("amount", 0.01, 1000000),
        freshness_check(max_age="24h"),
        volume_check(min_rows=100),
        matches_pattern("user_id", "^USR[0-9]{8}$")
    ],
    on_fail="abort"
)

# Test S3 user profiles source
s3_user_profiles_test: Test = Test(
    target=s3_user_profiles,
    checks=[
        schema_check(),
        not_null("user_id"),
        not_null("email"),
        unique("user_id"),
        unique("email"),
        matches_pattern("email", "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"),
        value_in("account_type", ["free", "premium", "enterprise"]),
        volume_check(min_rows=50)
    ],
    on_fail="abort"
)

# Test referential integrity between sources
referential_integrity_test: Test = Test(
    target=s3_transactions,
    checks=[
        referential_integrity("user_id", s3_user_profiles, "user_id")
    ],
    on_fail="abort"
)

# ============================================================================
# TEST DEFINITIONS - PostgreSQL Source
# ============================================================================

# Test PostgreSQL filter table
postgres_filters_test: Test = Test(
    target=postgres_filters,
    checks=[
        schema_check(),
        not_null("filter_id"),
        not_null("user_id"),
        unique("filter_id"),
        volume_check(min_rows=1),
        matches_pattern("user_id", "^USR[0-9]{8}$")
    ],
    on_fail="abort"
)

# ============================================================================
# TRANSFORMATION 1: JOIN AND AGGREGATE
# ============================================================================

# Join transactions with user profiles
s3_transactions.join(
    s3_user_profiles,
    "user_id",
    "user_id",
    type="inner"
)

# Transform: Add computed columns and filter
s3_transactions
    .select(
        "transaction_id",
        "user_id",
        "email",
        "amount",
        "category",
        "account_type",
        "country",
        "region",
        "timestamp"
    )
    .where("amount" > 0)
    .cast("timestamp" to datetime)

# Aggregate by user and category
aggregated_transactions: Source() = s3_transactions
    .group_by("user_id", "category", "account_type")
    .agg("amount", "sum", as="total_amount")
    .agg("transaction_id", "count", as="transaction_count")
    .agg("amount", "avg", as="avg_amount")
    .agg("amount", "max", as="max_amount")

# Test aggregated data before filtering
aggregated_test: Test = Test(
    target=aggregated_transactions,
    checks=[
        not_null("user_id"),
        not_null("total_amount"),
        value_range("total_amount", 0.01, 10000000),
        value_range("transaction_count", 1, 100000),
        custom(lambda row: row["avg_amount"] <= row["max_amount"]),
        volume_check(min_rows=10)
    ],
    on_fail="abort"
)

# ============================================================================
# TRANSFORMATION 2: FILTER BASED ON POSTGRESQL DATA
# ============================================================================

# Extract user IDs from PostgreSQL filter table
postgres_user_ids: string[] = []

# Iterate through PostgreSQL rows and collect user_ids to filter
for filter_row in postgres_filters:
    postgres_user_ids.append(filter_row["user_id"])

# Filter aggregated transactions: drop rows matching PostgreSQL filter list
# Keep only transactions from users NOT in the filter list
aggregated_transactions
    .where("user_id" not in postgres_user_ids)

# Alternative approach using anti-join (more performant for large datasets)
# aggregated_transactions.anti_join(postgres_filters, "user_id", "user_id")

# Add audit columns
aggregated_transactions
    .add_column("filtered_at", now())
    .add_column("pipeline_run_id", generate_uuid())
    .add_column("filter_count", len(postgres_user_ids))

# Test filtered aggregated data
filtered_aggregated_test: Test = Test(
    target=aggregated_transactions,
    checks=[
        not_null("user_id"),
        not_null("total_amount"),
        not_null("filtered_at"),
        not_null("pipeline_run_id"),
        volume_check(min_rows=5),
        # Ensure no filtered users remain
        custom(lambda row: row["user_id"] not in postgres_user_ids)
    ],
    on_fail="abort"
)

# ============================================================================
# SINK DEFINITIONS
# ============================================================================

# BigQuery sink for aggregated transactions
bq_aggregated_sink: Sink(BigQuery) = Sink(
    project=project_id,
    dataset=dataset_name,
    table="aggregated_user_transactions",
    write_disposition="WRITE_TRUNCATE",  # Options: WRITE_APPEND, WRITE_TRUNCATE, WRITE_EMPTY
    create_disposition="CREATE_IF_NEEDED",
    credentials="path/to/service-account-key.json",
    schema={
        "user_id": string not null,
        "category": string not null,
        "account_type": string not null,
        "total_amount": float not null,
        "transaction_count": int not null,
        "avg_amount": float not null,
        "max_amount": float not null,
        "filtered_at": datetime not null,
        "pipeline_run_id": string not null,
        "filter_count": int not null
    }
)

# BigQuery sink for PostgreSQL filter data
bq_filters_sink: Sink(BigQuery) = Sink(
    project=project_id,
    dataset=dataset_name,
    table="applied_user_filters",
    write_disposition="WRITE_APPEND",
    create_disposition="CREATE_IF_NEEDED",
    credentials="path/to/service-account-key.json",
    schema={
        "filter_id": int not null,
        "user_id": string not null,
        "filter_reason": string,
        "created_at": datetime not null,
        "loaded_at": datetime not null,
        "pipeline_run_id": string not null
    }
)

# ============================================================================
# TASK DEFINITIONS WITH CONDITIONAL EXECUTION
# ============================================================================

# Task 1: Write aggregated transactions to BigQuery (primary task)
# Tests run automatically before execution
task_aggregated: Task = aggregated_transactions >> bq_aggregated_sink

# Augment PostgreSQL data with audit columns
postgres_filters
    .add_column("loaded_at", now())
    .add_column("pipeline_run_id", generate_uuid())

# Test PostgreSQL data before loading
postgres_load_test: Test = Test(
    target=postgres_filters,
    checks=[
        not_null("filter_id"),
        not_null("user_id"),
        not_null("loaded_at"),
        not_null("pipeline_run_id")
    ],
    on_fail="abort"
)

# Task 2: Write PostgreSQL filters to BigQuery (conditional on Task 1 success)
# This task only executes if task_aggregated completes successfully
task_filters: Task = postgres_filters >> bq_filters_sink

# ============================================================================
# DAG EXECUTION ORDER
# ============================================================================

# Chain tasks: task_filters executes ONLY after task_aggregated succeeds
task_aggregated >> task_filters

# ============================================================================
# EXECUTION & DEBUGGING
# ============================================================================

# Uncomment for debugging (bypasses tests and shows intermediate results)
# aggregated_transactions.show
# aggregated_transactions.schema

# Uncomment to run tests only without executing pipeline
# aggregated_test.run()
# filtered_aggregated_test.run()
# postgres_load_test.run()

# ============================================================================
# MONITORING & LOGGING
# ============================================================================

# Log pipeline completion
on_success:
    log("Pipeline completed successfully at " + now())
    log("Aggregated transactions written: " + task_aggregated.rows_written)
    log("Filter records written: " + task_filters.rows_written)

on_failure:
    log("Pipeline failed at " + now())
    log("Failed task: " + failed_task.name)
    log("Error: " + failed_task.error_message)
    alert("email:data-team@company.com", "Pipeline Failure: " + failed_task.error_message)
