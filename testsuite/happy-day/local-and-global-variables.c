#include <stdio.h>

int glob_int = 60;
float glob_float = 2.58;
char glob_char = 'A';

int main(int argc, char* arv[]) {
    int loc_int = 375;
    float loc_float = 2.33356;
    char loc_char = 'a';

    printf("Global int: %d\n", glob_int);
    printf("Global float: %f\n", glob_float);
    printf("Global char: %c\n", glob_char);

    printf("Local int: %d\n", loc_int);
    printf("Local float: %f\n", loc_float);
    printf("Local char: %c\n", loc_char);
    return 0;
}