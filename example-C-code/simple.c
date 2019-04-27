#include <stdio.h>

int main() {
    int a = 5;
//    int *ptr_to_a = &a;
//    int b = *ptr_to_a;
    int b = a;
    printf("%d\n", a);
    printf("%d\n", b);
    return 0;
}