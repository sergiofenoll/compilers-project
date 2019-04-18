int main(int argc, char* argv[]) {
    int a = 1;
    int b;
    if (a == 1) {
        b = 5;
    }
    else if (a == 2) {
        b = 6;
    }
    else {
        b = 7;
    }
    int c;
    c = a ? b : 1;
    return 0;
}