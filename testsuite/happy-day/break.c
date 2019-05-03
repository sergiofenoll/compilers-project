#include <stdio.h>

int main() {
    int counter = 0;
    while(1) {
        if (counter >= 5) {
            break;
        }
        counter += 1;
        printf("Iteration %d\n", counter);
    }

    for (int i=1; i < 1000; i += 1) {
        if (i >= 5) {
            break;
        }
        printf("Iteration %d\n", i);
    }
    return 0;
}
