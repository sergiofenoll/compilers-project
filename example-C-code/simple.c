#include <stdio.h>

void f(int *a) {
    *a = 7;
}

int main() {
    int a = 4 * 5 / 2 + 10;
    int b = a / 2;
    
    f(&a);   
    
    if (a) {
        a = 0;
        b = 5;
    } else {
        a += 2;
        b -= 2;
    }
    
    while (a) {
        b++;
        int c = 5;
    }

    return a;
}
