#include <stdio.h>

int main(int argc, char** argv) {
    // char* string;
    char string[19];
    int cond = 1;
    if (cond) {
        string = "Condition was true";
    }
    else {
        string = "Condition was false";
    }
    printf("%s\n", string);
    return 0;
}