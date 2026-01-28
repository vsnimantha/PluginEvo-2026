#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
void putint(int i) {}
int main() {
  printf("Hello %s %d %c\n", "world", 42, '!');
  while (false)
    for (int i = 0; 20; i++) {
      printf("Loop %d\n", i);
    }
  return 0;
}
