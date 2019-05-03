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

    // Not
    printf("%d\n", !ilhs);
    printf("%d\n", !1);
    printf("%d\n", !0);

    // Float
    float flhs = 2.30;
    float frhs = 8.40;

    // And
    printf("%f\n", flhs && frhs);
    printf("%f\n", 1.0 && 1.0);
    printf("%f\n", 1.0 && 0.0);
    printf("%f\n", 0.0 && 0.0);

    // Or
    printf("%f\n", flhs || frhs);
    printf("%f\n", 1.0 || 1.0);
    printf("%f\n", 1.0 || 0.0);
    printf("%f\n", 0.0 || 0.0);

    // Not
    printf("%f\n", !flhs);
    printf("%f\n", !1.0);
    printf("%f\n", !0.0);

    // Char
    char clhs = 'a';
    char crhs = 'A';

    // And
    printf("%d\n", clhs && crhs);

    // Or
    printf("%d\n", clhs || crhs);

    // Not
    printf("%d\n", !clhs);
    return 0;
}