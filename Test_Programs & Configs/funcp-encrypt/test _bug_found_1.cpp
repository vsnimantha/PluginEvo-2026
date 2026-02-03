#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

template <typename T>
class Container {
public:
    Container() = default;

    void add(const T& item) {
        items.push_back(item);
    }

    void printAll() const {
        for (const auto& item : items) {
            std::cout << item << " ";
        }
        std::cout << "\n";
    }

    T getMax() const {
        if (items.empty()) {
            throw std::runtime_error("Empty container");
        }
        return *std::max_element(items.begin(), items.end());
    }

private:
    std::vector<T> items;
};

int factorial(int n) {
    if (n <= 1)
        return 1;
    else
        return n * factorial(n - 1);
}

int main() {
    try {
        Container<int> intContainer;
        for (int i = 1; i <= 10; ++i) {
            intContainer.add(i);
        }
        intContainer.printAll();

        std::cout << "Max: " << intContainer.getMax() << "\n";
        std::cout << "Factorial of 5: " << factorial(5) << "\n";

        Container<std::string> stringContainer;
        stringContainer.add("apple");
        stringContainer.add("banana");
        stringContainer.add("cherry");
        stringContainer.printAll();

    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << "\n";
    }
    return 0;
}
