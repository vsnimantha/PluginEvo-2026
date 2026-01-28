#include <iostream>
using namespace std;

// Function to calculate the sum of digits
int sumOfDigits(int num) {
    int sum = 0;
    while (num != 0) {
        sum += num % 10;
        num /= 10;
    }
    return sum;
}

int main() {
    int number=10;
    // cout << "Enter a number: ";
    // cin >> number;

    int sum = sumOfDigits(number);
    cout << "Sum of digits: " << sum << endl;

    return 0;
}