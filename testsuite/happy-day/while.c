#include <stdio.h>

int main() {
    int cond = 1;
    int counter = 0;
    while(cond) {
        if (counter >= 5) {
            cond = 0;
        }
        counter += 1;
        printf("Iteration %d\n", counter);
    }

    while(0) {
        printf("This will never be printed!\n");
    }
    return 0;
}