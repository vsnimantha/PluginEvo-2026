#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
void putint(int i) { printf("%d", i); }
int main() {
  printf("Hello %s %d %c\n", "world", 42, '!');
  while (false) {
    int delta[19][17] = {12, 18, 1,  6, 7, 21, 1, 10, 11, 17,
                         10, 20, 20, 4, 2, 7,  1, 7,  11};
    for (int i = 0; i < 19; i++) {
      printf("Conditional %s\n", "branch");
    }
  }
  return 1;
}
