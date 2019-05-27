#include <stdio.h>

void f(int* a) {
    *a = 7;
}

int main() {
    int a = 4 + 1;
    f(&a);
    return a;
}
