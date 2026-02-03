#include <iostream>
using namespace std;

int main() {
    for (int i = 1; i <= 5; i++) {
        if (i % 2 == 0)
            cout << i << " is even" << endl;
        else
            cout << i << " is odd" << endl;
    }

    int counter = 1;

    // A do-while loop runs the body at least once
    do {
        cout << "Counter is: " << counter << endl;
        counter++;  // increment
    } while (counter <= 5);  // condition checked after each iteration
    return 0;
}
