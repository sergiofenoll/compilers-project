int g = 1;

float f() {
    float r = 1.23;
    return r;
}

int main(int argc, char* argv[]) {
    int a;
    int b = 5;
    
    if (g <= 0) {
        a = 1;
    } else if (g > 0 && b < 10) {
        a = b * 2;
    } else if (g > 0 && b >= 10) {
        a = b - 5;
    } else {
        a = (b + g) / 2;
    }
      
} 
