#include <stdio.h>

int main() {
    int a = 4 * 5 / 2 + 10;
    int b = a / 2;
    
    if (a) {
        a = 0;
        b = 5;
    } else {
        a += 2;
        b -= 2;
    }

    return a;
}
