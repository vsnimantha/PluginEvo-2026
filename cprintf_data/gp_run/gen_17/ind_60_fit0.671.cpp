#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
int main() {
  int i = 0;
  for (int i = 0; 0; i++) {
    printf("Loop %d\n", i);
  }
  if (printf("Conditional %s\n", "branch")) {
    printf("Inside if\n");
  }
  return 0;
}
