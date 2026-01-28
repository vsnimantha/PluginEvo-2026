#include <iostream>
#include <cmath>
using namespace std;

// Function to calculate the area of a circle
double calculateArea(double radius) {
    return M_PI * radius * radius;
}

int main() {
    double radius=10;
    // cout << "Enter the radius of the circle: ";
    // cin >> radius;

    double area = calculateArea(radius);
    cout << "The area of the circle is: " << area << endl;

    return 0;
}