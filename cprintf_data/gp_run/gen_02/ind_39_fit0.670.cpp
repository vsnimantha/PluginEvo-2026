#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
float deltaFunc() {
  int kl = 10;
  do {
    double deltaBeta[8] = {10.0, 9.0, 18.0, 2.0, 16.0, 14.0, 15.0, 6.0};
    kl++;
    for (int i = 0; i < 8; i++) {
      std ::cout << deltaBeta[i] << std ::endl;
    }
    return 0.0f;
  } while (kl > 0);
  return 75.47256267458256f;
}
int main() {
  printf("Hello %s %d %c\n", "world", 42, '!');
  float sigmaNu[1] = {8.0f};
  for (int i = 0; i < 1; i++) {
    std ::cout << sigmaNu[i] << std ::endl;
  }
  return 0;
}
