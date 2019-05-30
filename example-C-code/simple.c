int f() {
    return 1 + 1;
}

int main() {

    int a = 5;
    int b = 0;
    
    if (a && b) {
        a *= b;
    } else {
        a += b;
    }
    
    return a;
}
