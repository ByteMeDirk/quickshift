import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: quickshift <pipeline.qs>")
        sys.exit(1)
    path = sys.argv[1]
    # Insert parsing and execution logic
    print(f"Executing pipeline: {path}")
