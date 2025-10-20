# Quickshift DSL

A Python-based Domain-Specific Language (DSL) for data management with a complete compiler pipeline including lexer, parser, semantic analyzer, and LLVM IR code generator.

## Features

- **Lexer**: Tokenizes source code into a stream of tokens
- **Parser**: Builds an Abstract Syntax Tree (AST) from tokens using recursive descent parsing
- **Semantic Analyzer**: Performs type checking and semantic validation
- **LLVM Code Generator**: Generates LLVM Intermediate Representation (IR) from the AST

## Language Features

### Data Types
- `int` - 32-bit integers
- `float` - Floating-point numbers
- `bool` - Boolean values (true/false)
- `string` - String literals
- `void` - Void type for functions

### Variables
```
let x: int = 10;        // Variable declaration with type
let y = 20;             // Type inference
const PI: float = 3.14; // Constant declaration
```

### Functions
```
function add(a: int, b: int) -> int {
    return a + b;
}

function greet() -> void {
    // No return value
}
```

### Control Flow
```
// If-else statements
if (x > 0) {
    // then block
} else {
    // else block
}

// While loops
while (i < 10) {
    i = i + 1;
}

// For loops
for (let i: int = 0; i < 10; i = i + 1) {
    // loop body
}
```

### Operators

**Arithmetic**: `+`, `-`, `*`, `/`, `%`

**Comparison**: `<`, `<=`, `>`, `>=`, `==`, `!=`

**Logical**: `and`, `or`, `not`

### Comments
```
// Single-line comment

/* Multi-line
   comment */
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Compile a Quickshift program

```bash
python quickshift_compiler.py examples/fibonacci.qs
```

### Command-line options

```bash
python quickshift_compiler.py <input.qs> [options]

Options:
  -o, --output FILE   Output LLVM IR to file
  -t, --tokens        Show tokens
  -a, --ast           Show AST
  --no-ir            Don't show LLVM IR
```

### Examples

Compile and show LLVM IR:
```bash
python quickshift_compiler.py examples/arithmetic.qs
```

Compile and save IR to file:
```bash
python quickshift_compiler.py examples/fibonacci.qs -o fibonacci.ll
```

Show tokens and AST:
```bash
python quickshift_compiler.py examples/loops.qs -t -a
```

## Running Tests

```bash
python -m unittest discover tests
```

Run specific test file:
```bash
python -m unittest tests.test_lexer
python -m unittest tests.test_parser
python -m unittest tests.test_semantic_analyzer
python -m unittest tests.test_codegen
```

## Example Programs

### Arithmetic (`examples/arithmetic.qs`)
```
let x: int = 10;
let y: int = 20;
let sum: int = x + y;

function add(a: int, b: int) -> int {
    return a + b;
}
```

### Fibonacci (`examples/fibonacci.qs`)
```
function fibonacci(n: int) -> int {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}
```

### Loops (`examples/loops.qs`)
```
function factorial(n: int) -> int {
    let result: int = 1;
    for (let i: int = 1; i <= n; i = i + 1) {
        result = result * i;
    }
    return result;
}
```

## Architecture

### Compiler Pipeline

1. **Lexical Analysis (Lexer)**: Converts source code into tokens
2. **Syntax Analysis (Parser)**: Builds an AST from tokens
3. **Semantic Analysis**: Type checking and validation
4. **Code Generation**: Generates LLVM IR from the AST

### Project Structure

```
quickshift/
├── quickshift/
│   ├── __init__.py
│   ├── token_types.py      # Token definitions
│   ├── lexer.py            # Lexical analyzer
│   ├── ast_nodes.py        # AST node definitions
│   ├── parser.py           # Parser
│   ├── semantic_analyzer.py # Semantic analyzer
│   └── codegen.py          # LLVM code generator
├── tests/
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_semantic_analyzer.py
│   └── test_codegen.py
├── examples/
│   ├── arithmetic.qs
│   ├── fibonacci.qs
│   ├── loops.qs
│   └── conditionals.qs
├── quickshift_compiler.py  # Main compiler entry point
├── requirements.txt
└── README.md
```

## Dependencies

- Python 3.7+
- llvmlite >= 0.41.0

## License

See LICENSE file for details.
