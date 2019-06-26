#include <stdio.h>

int main(int argc, char** argv) {
    // Integer
    int ilhs = 10;
    int irhs = 4;

    // And
    printf("%d\n", ilhs && irhs);
    printf("%d\n", 1 && 1);
    printf("%d\n", 1 && 0);
    printf("%d\n", 0 && 0);

    // Or
    printf("%d\n", ilhs || irhs);
    printf("%d\n", 1 || 1);
    printf("%d\n", 1 || 0);
    printf("%d\n", 0 || 0);

    // Char
    char clhs = 'a';
    char crhs = 'A';

    // And
    printf("%d\n", clhs && crhs);

    // Or
    printf("%d\n", clhs || crhs);
    return 0;
}