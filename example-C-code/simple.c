#include <stdio.h>

void f(int* k) {
    *k = 69;
}

int main() {

    int a = 5;
    int b = 6;
    b = a;
    int d = b;
    float c = 4.0 + 5.0;
    // f(&a);
    /*
    int b = a * 2;
    f(&b);
    int c = b / 2;
    f(&c);
    */
    printf("%f\n", a);
    return 0;
}
