#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
int main() {
  int kl = 5;
  do {
    int betaKappa[1] = {12};
    kl++;
    for (int i = 0; i < 1; i++) {
      std ::cout << betaKappa[i] << std ::endl;
    }
  } while (kl < 20);
  printf("Empty string\n");
  printf("One int: %d\n", 1);
  printf("Two ints: %d %d\n", 1, 2);
  printf("Extra args ignored: %d %d\n", 1, 2);
  return 0;
}
