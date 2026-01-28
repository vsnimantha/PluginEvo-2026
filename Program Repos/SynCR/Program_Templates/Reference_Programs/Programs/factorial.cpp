#include <iostream>
using namespace std;

// Recursive function to calculate factorial
int factorial(int n) {
    if (n == 0 || n == 1)
        return 1;
    else
        return n * factorial(n - 1);
}

int main() {
    int number=10;
    // cout << "Enter a number: ";
    // cin >> number;

    int result = factorial(number);
    cout << "Factorial of " << number << " is: " << result << endl;

    return 0;
}