// Template_9.tmpl
#include <iostream>
#include <stdio.h>

using namespace std;

// Handler for %d
void putint(int i) { printf("%d", i); }

int main(void) {
  printf("Hello %s %d %c\n", "world", 42, '!');
  int ij = 20;
  while (ij > 10) {
    double etaIota = 11 * 4;
    ij++;
  }
  return 0;
}