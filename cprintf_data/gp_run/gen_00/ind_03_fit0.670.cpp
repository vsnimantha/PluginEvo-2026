#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
int main() {
  int kl = 0;
  do {
    double rhoPsi = 16 / 17;
    kl++;
  } while (kl < 5);
  printf("Empty string\n");
  printf("One int: %d\n", 1);
  printf("Two ints: %d %d\n", 1, 2);
  printf("Extra args ignored: %d %d\n", 1, 2);
  return 0;
}
