#include <stdio.h>

int main() {
    int a;
    for (int i = 1; i < 5; i += 1) {
        printf("Iteration %d\n", i);
    }

    for (int i = 1; i < 5; i += 1) {
        int i = 0;
        printf("%d", i);
    }
    printf("\n");

    for (int i = 0; i < 10; i += 1) printf("%d", i);
    printf("\n");

    return 0;
}