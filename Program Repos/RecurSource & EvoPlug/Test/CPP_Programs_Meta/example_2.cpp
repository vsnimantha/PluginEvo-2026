#include <iostream>
#include <string>
using namespace std;


class Car {
public:
    string brand= "Toyota";
    int year;

    int display() {
        cout << brand << endl;
        cout << brand << " " << year << endl;
        cout << brand << " " << year << endl;
        cout << brand << " " << year << endl;
        cout << brand << " " << year << endl;
        cout << brand << " " << year << endl;
        cout << brand << " " << year << endl;
        cout << brand << " " << year << endl;
        cout << brand << " " << year << endl;
        cout << brand << " " << year << endl;
        return 0;
    }

};

class Huththi{
public:
    string name;
    int age;

    void display() {
        cout << "Name: " << name << ", Age: " << age << endl;
    }
private:
    int pakaya; 
    string hutti;
};


int main() {
    Car myCar;
    myCar.brand = "Toyota";
    myCar.year = 2020;
    myCar.display();
    return 0;
}
