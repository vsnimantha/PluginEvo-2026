#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
int main() {
  if (true) {
    {
      float sigmaNu[1] = {8.0f};
      for (int i = -2; i < 1; i++) {
      }
      return 1;
    }

  } else {
    printf("Debug output generated");
  }
  for (int i = 0; i < 3; i--) {
    printf("Loop %d\n", i);
  }
  if (printf("%d", "branch")) {
  }
  return -2;
}
