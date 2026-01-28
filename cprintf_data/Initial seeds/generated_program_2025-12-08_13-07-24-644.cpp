// Template_3.tmpl
#include <iostream>
#include <stdio.h>
using namespace std;

int main() {
  int kl = 0;
  do {
    double rhoPsi = 16 / 17;
    kl++;
  } while (kl < 5);
  printf("Empty string\n");                    // safe literal
  printf("One int: %d\n", 1);                  // valid
  printf("Two ints: %d %d\n", 1, 2);           // valid
  printf("Extra args ignored: %d %d\n", 1, 2); // safe, matches specifiers
  return 0;
}
