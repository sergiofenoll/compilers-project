#include <stdio.h>

int main(int argc, char** argv) {
    // Integer
    int ilhs = 10;
    int irhs = 4;

    // Smaller than or equal
    printf("%d\n", ilhs <= irhs);
    printf("%d\n", 2 <= 3);
    printf("%d\n", 4 <= 3);

    // Larger than or equal
    printf("%d\n", ilhs >= irhs);
    printf("%d\n", 3 >= 2);
    printf("%d\n", 3 >= 7);

    // Not equals
    printf("%d\n", ilhs != irhs);
    printf("%d\n", 2 != 2);
    printf("%d\n", 2 != 1);

    // Float
    float flhs = 2.30;
    float frhs = 8.40;

    // Smaller than or equal
    printf("%f\n", flhs <= frhs);
    printf("%f\n", 2.2 <= 2.6);
    printf("%f\n", 7.2 <= 2.6);

    // Larger than or equal
    printf("%f\n", flhs >= frhs);
    printf("%f\n", 4.20 >= 2.4);
    printf("%f\n", 4.20 >= 5.6);

    // Not equals
    printf("%f\n", flhs != frhs);
    printf("%f\n", 2.21 != 2.21);
    printf("%f\n", 2.21 != 2.29);

    // Char
    char clhs = 'a';
    char crhs = 'A';

    // Smaller than or equal
    printf("%d\n", clhs <= crhs);
    printf("%d\n", 'a' <= 'b');
    printf("%d\n", 'A' <= 'b');

    // Larger than or equal
    printf("%d\n", clhs >= crhs);
    printf("%d\n", 'A' >= 'b');
    printf("%d\n", 'a' >= 'c');

    // Not equals
    printf("%d\n", clhs != crhs);
    printf("%d\n", 'z' != 'z');
    printf("%d\n", 'z' != 'A');
    return 0;
}