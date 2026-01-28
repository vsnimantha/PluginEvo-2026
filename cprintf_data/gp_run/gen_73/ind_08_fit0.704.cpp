#include <cstdio>
#include <iostream>
#include <stdlib.h>
using namespace std;
int kappaFunc() {
  int kl = 5;
  do {
    return 66;
  } while (20);
  return 0;
  do {
    kl++;
    return 66;
  } while (kl < 20);
}
int kl = 15;
int main() {
  kappaFunc();
  printf("Debug output generated");
  {
    int kl = 15;
    do {
      kl++;
    } while (printf("Hex: %x\n", 253));
    printf("Empty string\n");
    printf("Two ints: %d %d\n", 1, 2);
    printf("Extra args ignored: %d %d\n", 1, 2);
    return -2;
  }
}
