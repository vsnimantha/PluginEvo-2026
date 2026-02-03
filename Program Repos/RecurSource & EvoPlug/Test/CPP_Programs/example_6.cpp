#include <iostream>
#include <vector>

template<typename T>

// class Foo {
//     T value;
// };

class Matrix {
    std::vector<std::vector<T>> data;
public:
    Matrix(int rows, int cols, T init = T()) : data(rows, std::vector<T>(cols, init)) {}

    std::vector<T>& operator[](int index) { return data[index]; }

    Matrix<T> operator+(const Matrix<T>& other) {
        Matrix<T> result(data.size(), data[0].size());
        for (size_t i = 0; i < data.size(); ++i)
            for (size_t j = 0; j < data[i].size(); ++j)
                result[i][j] = data[i][j] + other.data[i][j];
        return result;
    }

    void print() {
        for (const auto& row : data) {
            for (const auto& val : row)
                std::cout << val << " ";
            std::cout << "\n";
        }
    }
};

int main() {
    Matrix<int> m1(2, 2, 1);
    Matrix<int> m2(2, 2, 2);
    Matrix<int> m3 = m1 + m2;
    // m3.print();
    return 0;
}
