#include <iostream>
#include <cstdlib>
#include <ctime>
using namespace std;

// Function to generate a random number within a range
int generateRandomNumber(int min, int max) {
    return rand() % (max - min + 1) + min;
}

int main() {
    srand(time(0)); // Seed the random number generator

    int min, max;
    // cout << "Enter the range (min and max): ";
    // cin >> min >> max;
    max=100;
    min=1;

    int randomNumber = generateRandomNumber(min, max);
    cout << "Random number between " << min << " and " << max << ": " << randomNumber << endl;

    return 0;
}