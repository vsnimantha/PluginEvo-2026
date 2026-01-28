#include <cstdio>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
float sigmaNu[1] = {8.0f};
void putstring(const char *s) {}
int iotaFunc() {
  float nu[8] = {86.53313259417854f,
                 7.0f,
                 15.0f,
                 33.76557699969345f,
                 5.0f,
                 11.0f,
                 6.0f,
                 17.0f};
  for (int i = 0; i < 8; i++) {
    std ::cout << nu[i] << std ::endl;
  }
  return 0;
}
int main() {
  printf("Hello %s %d %c\n", "world", 42, '!');
  return 0;
}
