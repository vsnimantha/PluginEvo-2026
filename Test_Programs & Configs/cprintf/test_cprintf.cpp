#include <cstdio>
#include <string>

void test_literal_format() {
    std::printf("literal: a=%d b=%d\n", 1, 2);
}

void test_const_pointer_format() {
    const char *fmt = "const_ptr: x=%d y=%d\n";
    std::printf(fmt, 3, 4);
}

void test_static_array_format() {
    static const char fmt2[] = "static_array: p=%d q=%d\n";
    std::printf(fmt2, 5, 6);
}

void test_string_c_str_format() {
    std::string dyn = "string_c_str: r=%d s=%d\n";
    std::printf(dyn.c_str(), 7, 8);
}

int main() {
    test_literal_format();
    test_const_pointer_format();
    test_static_array_format();
    test_string_c_str_format();
    return 0;
}
