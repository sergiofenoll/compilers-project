
int main() {

    int a = 3;
    
    for (int i = 0; i < 3; i = i + 1) {
        a = a - 1;
        if (a == 1) {
            break;
        }
    }
    
    return a;
}

