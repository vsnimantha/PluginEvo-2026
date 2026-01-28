#include <iostream>
using namespace std;

// Recursive function to calculate the sum of first n natural numbers
int sumOfNaturalNumbers(int n) {
    // Base case: if n is 0, return 0
    if (n == 0) {
        return 0;
    }
    // Recursive case: add n to the sum of the first (n-1) natural numbers
    return n + sumOfNaturalNumbers(n - 1);
}

int main() {
    int n=10;
    // cout << "Enter a positive integer: ";
    // cin >> n;

    if (n < 0) {
        cout << "Please enter a positive integer." << endl;
    } else {
        int result = sumOfNaturalNumbers(n);
        cout << "Sum of first " << n << " natural numbers is: " << result << endl;
    }

    return 0;
}