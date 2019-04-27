#include <stdio.h>

int main() {
    int a = 5;
    int *ptr_to_a = &a;
    int b = *ptr_to_a;
    return 0;
}