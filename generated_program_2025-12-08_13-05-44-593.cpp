// Template_3.tmpl
#include <iostream>
#include <stdio.h>
using namespace std;

int main() {
  int kl = 15;
  do {
    std::cout << "1PKD3T498WL9Y5XVTXSC" << std::endl;
    kl++;
  } while (kl > 10);
  printf("Empty string\n");                    // safe literal
  printf("One int: %d\n", 1);                  // valid
  printf("Two ints: %d %d\n", 1, 2);           // valid
  printf("Extra args ignored: %d %d\n", 1, 2); // safe, matches specifiers
  return 0;
}
