#include <iostream>
using namespace std;

int main() {
    for (int i = 1; i <= 5; i++) {
        if (i % 2 == 0)
            cout << i << " is even" << endl;
        else
            cout << i << " is odd" << endl;
    }
    return 0;
}
