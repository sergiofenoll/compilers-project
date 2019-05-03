#include <stdio.h>

void voidFunc() {
    printf("This function has no arguments\n");
}

int intFunc(int a) {
    printf("This function has argument 'a':%d\n", a);
    return a;
}

float floatFunc(float a) {
    printf("This function has argument 'a':%f\n", a);
    return a;
}

char charFunc(char a) {
    printf("This function has argument 'a':%c\n", a);
    return a;
}

int main(int argc, char* argv[]) {
    intFunc(60);
    floatFunc(5.53);
    charFunc('q');
    return 0;
}