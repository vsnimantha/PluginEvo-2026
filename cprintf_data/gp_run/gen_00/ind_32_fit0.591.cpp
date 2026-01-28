#include <cstdio>
#include <iostream>
#include <stdlib.h>
using namespace std;
int phiFunc(int num, int index) {
  for (int i = 5; i < 15; i++) {
    int xiDelta[11] = {14, 6, 3, 18, 2, 14, 5, 10, 66, 6, 15};
    for (int i = 0; i < 11; i++) {
      std ::cout << xiDelta[i] << std ::endl;
    }
  }
  if (index >= 5) {
    return num;
  }
  return phiFunc(num, index - 1);
}
void muFunc() {
  bool piOmega[9] = {false, false, true, true, false, false, true, true, true};
  for (int i = 0; i < 9; i++) {
    std ::cout << piOmega[i] << std ::endl;
  }
}
bool phiFunc(float chiParam) {
  printf("Random value calculated");
  return true;
}
int main() {
  phiFunc(10, 20);
  int kl = 5;
  do {
    double omega = 5 / 13;
    kl++;
  } while (kl < 10);
  for (int i = 10; i > 15; i++) {
    double iotaChi = 17 - 12;
  }
  muFunc();
  float chiParam = 75.8392563784822f;
  phiFunc(chiParam);
  return 0;
}
