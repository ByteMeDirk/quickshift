# Simple Quickshift pipeline example

# Read CSV data
source: Source(csv) = Source(
    path="file://input/users.csv",
    schema={"id": int not null, "name": string not null, "age": int}
)

# Define output sink
sink: Sink(parquet) = Sink(path="file://output/users.parquet")

# Test source data
test: Test = Test(
    target=source,
    checks=[
        schema_check(),
        not_null("id"),
        unique("id"),
        value_range("age", 0, 120)
    ]
)

# Transform and pipeline
source.select("id", "name", "age").where("age" >= 18)
source >> sink
