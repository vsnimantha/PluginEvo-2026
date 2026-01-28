#include <iostream>
using namespace std;

// Function to check if a number is even or odd
string checkEvenOdd(int num) {
    if (num % 2 == 0)
        return "Even";
    else
        return "Odd";
}

int main() {
    int number=10;
    // cout << "Enter a number: ";
    // cin >> number;

    string result = checkEvenOdd(number);
    cout << "The number is " << result << endl;

    return 0;
}