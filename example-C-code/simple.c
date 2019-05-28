void f(int* k) {
    *k = 69;
}

int main() {

    int a = 5 + 5;
    f(&a);
    int b = a * 2;
    f(&b);
    int c = b / 2;
    f(&c);
    return 0;
}
