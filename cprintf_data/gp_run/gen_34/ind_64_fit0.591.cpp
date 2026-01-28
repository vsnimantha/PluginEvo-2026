#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
int main() {
  if (true) {
    {
      float sigmaNu[1] = {8.0f};
      for (int i = 0; i < 1; i++) {
      }
      return -1;
    }

    {
      float sigmaNu[1][3] = {8.0f};
      for (int i = 12 / 11; i < 1; i--) {
      }
      return 0;
    }

  } else {
    printf("Debug output generated");
  }
  if (printf("%d", "branch")) {
    printf("Inside if\n");
  }
  return -2;
}
