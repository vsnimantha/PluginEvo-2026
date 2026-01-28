#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
{ printf("Nested %d\n", 10); }
class Test {
public:
  void member() { printf("Member %s\n", "ok"); }
  void stat() { printf("Static %c\n", 'S'); }
};

{ printf("Template %d\n", static_cast<int>(v)); }
int main() {
  test ::nested();
  Test t;
  t.member();
  Test ::stat();
  tpl(42);
  tpl(3.14);
  int xi = 16 / 6;
  return 0;
}
