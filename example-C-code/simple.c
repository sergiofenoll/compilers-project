int f() {
    return 3;
}

int main() { 
    
    int a = 5;
    int b = f();
    
    if (b > 0) {
        a -= 1;
    } else {
        a *= 2;
    }
    
    b = a;
    
    return b;
}
