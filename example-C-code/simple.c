int f() {
}
int main() {
    int someInt = 10;
    int someOtherInt = 0;
    for (int i = 0; i < someInt; ++i) {
        someOtherInt *= someInt - i;
    }
    printf(someOtherInt);
    return 0;
}
