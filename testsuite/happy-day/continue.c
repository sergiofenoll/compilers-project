#include <stdio.h>

int main() {
    int counter = 0;
    while(1) {
        if (counter < 3) {
            counter += 1;
            continue;
        }
        printf("Iteration %d\n", counter);
		break;
    }

    for (int i=1; i < 5; i += 1) {
        if (i < 3) {
            continue;
        }
        printf("Iteration %d\n", i);
    }
    return 0;
}
