#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
void putchar(char c) { fputc(c, stdout); }
int main() {
  printf("Hello %s %d %c\n", "world", 42, '!');
  double deltaBeta[1] = {6.0};
  for (int i = 0; i < 1; i++) {
    std ::cout << deltaBeta[i] << std ::endl;
  }
  return 0;
}
