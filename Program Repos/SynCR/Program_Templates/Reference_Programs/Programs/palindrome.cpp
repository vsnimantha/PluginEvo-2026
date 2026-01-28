#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

// Function to check if a string is a palindrome
bool isPalindrome(string str) {
    string reversedStr = str;
    reverse(reversedStr.begin(), reversedStr.end());
    return str == reversedStr;
}

int main() {
    string input="Apple";
    // cout << "Enter a string: ";
    // cin >> input;

    if (isPalindrome(input))
        cout << "The string is a palindrome." << endl;
    else
        cout << "The string is not a palindrome." << endl;

    return 0;
}