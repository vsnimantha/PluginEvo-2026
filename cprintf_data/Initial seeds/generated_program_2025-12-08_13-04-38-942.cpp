// Template_5.tmpl
#include <iostream>
#include <stdio.h>
using namespace std;

namespace test {
void nested() { printf("Nested %d\n", 10); }
} // namespace test

class Test {
public:
  void member() { printf("Member %s\n", "ok"); }
  static void stat() { printf("Static %c\n", 'S'); }
};

template <typename T> void tpl(T v) {
  printf("Template %d\n", static_cast<int>(v));
}

int main() {
  test::nested();
  Test t;
  t.member();
  Test::stat();
  tpl(42);
  tpl(3.14);

  int xi = 16 / 6;
  return 0;
}
