#include <stdio.h>


void main() {

    int a[2] = {1, 2};
    int b = 0;
    int c = a[b + 1];
    printf("%d\n", c);
    return 0;
    
}

