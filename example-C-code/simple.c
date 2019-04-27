#include <stdio.h>


int main() {
    int a = 5;
    int *p = &a;
    int **pp = &p;
    int b = *p;
    int c = **pp;

    printf("%p\n", &a);
    printf("%p\n", p);
    printf("%p\n", *pp);

    printf("%d\n", a);
    printf("%d\n", b);
    printf("%d\n", c);
    return 0;
}
