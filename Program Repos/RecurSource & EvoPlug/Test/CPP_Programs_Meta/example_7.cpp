#include <iostream>
#include <fstream>
#include <string>


int main() {
    std::ofstream out("test.txt");
    if (!out) {
        std::cerr << "Failed to open file for writing\n";
        return 1;
    }
    out << "Hello, file!\n";
    out.close();

    std::ifstream in("test.txt");
    if (!in) {
        std::cerr << "Failed to open file for reading\n";
        return 1;
    }

    std::string line;
    while (std::getline(in, line)) {
        std::cout << "Read: " << line << "\n";
    }
    in.close();
    return 0;


}
