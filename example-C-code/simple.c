#include <stdio.h>

int fib(int n) {
    if (n <= 2) {
        return 1;
    }
    int f = fib(n - 2) + fib(n - 1);
    printf("%d\n", f);
    return f;
}

int main() {
    fib(6);
    return 0;
}
