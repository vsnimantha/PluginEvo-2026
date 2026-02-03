#include <iostream>
using namespace std;

int add(int a, int b) {
    return a + b;
}

double add(double a, double b) {
    return a + b;
}

int main() {
    cout << "Int add: " << add(2, 3) << endl;
    cout << "Double add: " << add(2.5, 3.1) << endl;
    return 0;
}
