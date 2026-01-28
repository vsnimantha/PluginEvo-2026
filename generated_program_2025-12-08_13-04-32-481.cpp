// Template_27.tmpl
#include <cstdio>
#include <iostream>
#include <stdlib.h>
using namespace std;

int tauFunc(int num, int index) {
  double epsilon = 16 * 11;
  if (index >= 5) {
    return num;
  }
  return tauFunc(num, index - 1);
}
void nuFunc() { std::cout << "Debug output generated" << std::endl; }
float upsilonFunc(double tauSigmaParam) {
  printf("Exiting function");
  return 0.0f;
}

int main() {

  tauFunc(10, 20);
  int kl = 20;
  do {
    int alpha = 9 * 3;
    kl++;
  } while (kl >= 20);
  for (int i = 15; i > 20; i++) {
    std::cout << "Calculation finished" << std::endl;
  }

  nuFunc();
  double tauSigmaParam = 60.5850541527285;

  upsilonFunc(tauSigmaParam);

  int x = 2147483647; // INT_MAX
  int y = x + 1;      // Undefined behavior
  std::cout << y << "\n";
}
