#include <iostream>
using namespace std;

// Function to find the maximum of two numbers
int findMax(int a, int b) {
    return (a > b) ? a : b;
}

int main() {
    int num1, num2;
    num1 = 10;
    num2 = 20;
    // cout << "Enter two numbers: ";
    // cin >> num1 >> num2;

    int max = findMax(num1, num2);
    cout << "The maximum number is: " << max << endl;

    return 0;
}