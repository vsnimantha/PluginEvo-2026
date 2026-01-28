#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
int main() {
  if (true) {
  } else {
    printf("Debug output generated");
  }
  for (int i = 0; i < 3; i--) {
    printf("Loop %d\n", i);
  }
  {
    if (false) {
      string pi[2] = {"RadiantEcho", "RadiantEcho"};
      for (int i = 0; i < 2; i++) {
        std ::cout << pi[i] << std ::endl;
      }
    } else {
      double deltaEpsilon = 12 / 11;
    }
    for (int i = 0; i < 3; i++) {
      printf("Loop %d\n", i);
    }
    if (printf("Conditional %s\n", "branch")) {
      printf("Inside if\n");
    }
    return 0;
  }
  return 0;
}
