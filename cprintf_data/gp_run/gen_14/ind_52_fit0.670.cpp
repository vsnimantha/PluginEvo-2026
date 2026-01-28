#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
int main() {
  if (true) {
    {
      printf("Hello %s %d %c\n", "world", 42, '!');
      float sigmaNu[1] = {8.0f};
      for (int i = 0; i < 1; i++) {
        std ::cout << sigmaNu[i] << std ::endl;
      }
      return 1;
    }

  } else {
    printf("Debug output generated");
  }
  for (int i = 0; i < 3; i--) {
    printf("Loop %d\n", i);
  }
  if (printf("Conditional %s\n", "branch")) {
    printf("Inside if\n");
  }
  return 0;
}
