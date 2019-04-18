int main(int argc, char* argv[]) {
    int a = 1;
    int b;
    int d = a * 0;
    int d1 = 0 * a;
    int d2 = 1 * a;
    int d3 = a * 1;
    int d4 = 0 * 3;
    int d5 = 3 * 1;
    if (a == 1) {
        b = 5;
    }
    else if (a == 2) {
        b = a + 2;
    }
    else {
        b = 7;
    }
    int c;
    c = a ? b : 1;
    return 0;
    d -= 10; // Useless statement
}
