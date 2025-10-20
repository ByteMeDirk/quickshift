// Conditional example
function max(a: int, b: int) -> int {
    if (a > b) {
        return a;
    } else {
        return b;
    }
}

function abs(x: int) -> int {
    if (x < 0) {
        return -x;
    }
    return x;
}

function main() -> int {
    let a: int = -42;
    let b: int = 15;
    let maximum: int = max(abs(a), b);
    return maximum;
}
