// Comprehensive example showing all language features

// Function to compute GCD using Euclidean algorithm
function gcd(a: int, b: int) -> int {
    while (b != 0) {
        let temp: int = b;
        b = a % b;
        a = temp;
    }
    return a;
}

// Function to check if a number is prime
function is_prime(n: int) -> bool {
    if (n <= 1) {
        return false;
    }
    if (n <= 3) {
        return true;
    }
    
    let i: int = 2;
    while (i * i <= n) {
        if (n % i == 0) {
            return false;
        }
        i = i + 1;
    }
    return true;
}

// Function to compute nth Fibonacci number
function fib(n: int) -> int {
    if (n <= 1) {
        return n;
    }
    
    let a: int = 0;
    let b: int = 1;
    let result: int = 0;
    
    for (let i: int = 2; i <= n; i = i + 1) {
        result = a + b;
        a = b;
        b = result;
    }
    
    return result;
}

// Function to compute factorial
function factorial(n: int) -> int {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

// Main function
function main() -> int {
    const TEN: int = 10;
    let result: int = 0;
    
    // Test GCD
    let g: int = gcd(48, 18);
    result = result + g;
    
    // Test prime checking
    if (is_prime(17)) {
        result = result + 17;
    }
    
    // Test Fibonacci
    let f: int = fib(TEN);
    result = result + f;
    
    // Test factorial
    let fact: int = factorial(5);
    result = result + fact;
    
    return result;
}
