// Template_6.tmpl
#include <iostream>
#include <stdio.h>
using namespace std;

int main() {
  if (true) {
    double eta = 4 * 6;
  } else {
    printf("Debug output generated");
  }
  for (int i = 0; i < 3; i++) {
    printf("Loop %d\n", i);
  }
  if (printf("Conditional %s\n", "branch")) {
    printf("Inside if\n");
  }
  return 0;
}
