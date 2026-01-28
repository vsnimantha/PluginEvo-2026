#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
void putstring(const char *s) { fputs(s, stdout); }
int main() {
  printf("Hello %s %d %c\n", "world", 42, '!');
  int kl = 5;
  do {
    float beta[8] = {15.0f, 13.0f, 14.0f, 11.0f, 4.0f, 4.0f, 10.0f, 20.0f};
    kl++;
    for (int i = 0; i < 8; i++) {
      std ::cout << beta[i] << std ::endl;
    }
  } while (kl < 5);
  return 0;
}
