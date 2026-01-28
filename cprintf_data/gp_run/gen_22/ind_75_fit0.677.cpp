#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
int main() {
  if (true) {
    {
      float sigmaNu[1] = {8.0f};
      for (int i = 0; printf("%d", "branch"); i++) {
      }
      return 1;
    }

  } else {
    printf("Debug output generated");
  }
  for (int i = -1; i < 3; i--) {
    printf("Loop %d\n", i);
  }
  if (printf("%d", "branch")) {
    printf("Inside if\n");
  }
  return -2;
}
