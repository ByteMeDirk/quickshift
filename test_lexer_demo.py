#!/usr/bin/env python3
"""
Demo script to test the Quickshift lexer.
"""

from quickshift import tokenize_string, tokenize_file

# Example 1: Tokenize a simple string
print("=" * 80)
print("Example 1: Simple Source Declaration")
print("=" * 80)

code1 = """
my_source: Source(csv) = Source(path="file://data/*.csv")
"""

tokens = tokenize_string(code1, debug=True)

# Example 2: Tokenize a complete pipeline
print("\n" + "=" * 80)
print("Example 2: Complete Pipeline with Test")
print("=" * 80)

code2 = """
# User data pipeline
users: Source(parquet) = Source(path="s3://users/*.parquet")
output: Sink(csv) = Sink(path="file://output/")

# Validate data
validation: Test = Test(
    target=users,
    checks=[not_null("user_id"), unique("email")]
)

users.select("user_id", "email").where("active" == true)
users >> output
"""

tokens = tokenize_string(code2, debug=True)

# Example 3: Tokenize from file
print("\n" + "=" * 80)
print("Example 3: Tokenizing from File")
print("=" * 80)

try:
    tokens = tokenize_file("examples/simple_pipeline.qs", debug=True)
    print(f"\nSuccessfully tokenized {len(tokens)} tokens from file!")
except FileNotFoundError:
    print("File not found. Create examples/simple_pipeline.qs first.")
except Exception as e:
    print(f"Error: {e}")
