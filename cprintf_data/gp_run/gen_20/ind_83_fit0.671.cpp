#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
int main() {
  int i = 0;
  for (int i = 0; "Loop %d\n"; i++) {
    printf("Loop %d\n", i);
  }
  if (printf("Conditional %s\n", "branch")) {
    printf("Inside if\n");
  }
  return i < 3;
}
