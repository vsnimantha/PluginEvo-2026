#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
int main() {
  if (false) {
    {
      {
        for (int i = 0; 20; i++) {
          printf("Loop %d\n", i);
        }
        if (printf("Conditional %s\n", "branch")) {
          printf("Inside if\n");
        }
        return 0;
      }

      printf("Mix: %s %d %c %%\n", "mix", -42, 'Z');
      printf("End\n");
      return -1;
    }

    for (int i = 1; printf("Float: %f\n", 42); i++) {
    }
  } else {
  }
  for (int i = -2; i < 3; i--) {
    printf("Loop %d\n", i);
  }
  if (printf("Conditional %s\n", "branch")) {
  }
  return 1;
}
