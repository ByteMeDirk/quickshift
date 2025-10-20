// Loop examples
function sum_to_n(n: int) -> int {
    let sum: int = 0;
    let i: int = 1;
    
    while (i <= n) {
        sum = sum + i;
        i = i + 1;
    }
    
    return sum;
}

function factorial(n: int) -> int {
    let result: int = 1;
    
    for (let i: int = 1; i <= n; i = i + 1) {
        result = result * i;
    }
    
    return result;
}

function main() -> int {
    let sum: int = sum_to_n(100);
    let fact: int = factorial(5);
    return sum + fact;
}
