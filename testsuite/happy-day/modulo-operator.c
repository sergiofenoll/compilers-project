#include <stdio.h>

int main(int argc, char** argv) {
    // Integer
    int ilhs = 10;
    int irhs = 4;

    printf("%d\n", ilhs % irhs);

    // Char
    char clhs = 'a';
    char crhs = 'A';

    printf("%c\n", clhs % crhs);
    return 0;
}