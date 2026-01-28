// Template_3.tmpl
#include <iostream>
#include <stdio.h>
using namespace std;

int main() {
  int kl = 5;
  do {
    int betaKappa[1] = {12};
    kl++;
    for (int i = 0; i < 1; i++) {
      std::cout << betaKappa[i] << std::endl;
    }
  } while (kl < 20);
  printf("Empty string\n");                    // safe literal
  printf("One int: %d\n", 1);                  // valid
  printf("Two ints: %d %d\n", 1, 2);           // valid
  printf("Extra args ignored: %d %d\n", 1, 2); // safe, matches specifiers
  return 0;
}
