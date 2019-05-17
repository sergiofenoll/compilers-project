#include <stdio.h>

int main() {
    int counter = 0;
    while(counter < 4) {
        counter += 1;
        if (counter <= 3) {
            continue;
        }
        printf("Iteration %d\n", counter);
    }

    for (int i=0; i < 5; i += 1) {
        if (i <= 3) {
            continue;
        }
        printf("Iteration %d\n", i);
    }
    return 0;
}
