#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
void putchar(char c) { fputc(c, stdout); }
int main() {
  printf("Hello %s %d %c\n", "world", 42, '!');
  float sigmaNu[1] = {8.0f};
  for (int i = 0; i < 1; i++) {
    std ::cout << sigmaNu[i] << std ::endl;
  }
  return 0;
}
