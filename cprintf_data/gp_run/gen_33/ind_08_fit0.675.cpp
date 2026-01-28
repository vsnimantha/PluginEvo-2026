#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
int main() {
  if (true) {
    int kl = 5;

  } else {
  }
  for (int i = 2; i < 3; i--) {
    printf("Loop %d\n", i);
  }
  if (printf("%d", "branch")) {
    printf("Inside if\n");
  }
  return -2;
}
