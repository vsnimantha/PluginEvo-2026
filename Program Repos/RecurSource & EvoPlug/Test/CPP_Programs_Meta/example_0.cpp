#include <iostream>
using namespace std;

int pakaya(int a, int b) {
    return a + b;
}

int main() {
    int age;
    cout << "Enter your age: "<<endl;
    cin >> age;
    cout << "Enter your age: ";

    pakaya(1, 2);
    cout << "You are " << age << " years old." << endl;
    return 0;
}
