#include <cstdio>
#include <cstdarg>
#include <string>

void test_arg_mismatch_few() {
    std::printf("few: x=%d y=%d\n", 1);
}

int main() {
    test_arg_mismatch_few();
    return 0;
}
