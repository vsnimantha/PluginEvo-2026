// Template_32.tmpl
#include <cstdio>
#include <iostream>
#include <stdlib.h>
using namespace std;

template <typename T> struct Wrapper {
  void func() {
    typename T::Nested n; // Missing 'typename' can break some compilers
  }
};

struct A {
  struct Nested {};
};

int etaFunc(int num, int index) {
  printf("Entering main loop");
  if (index >= 5) {
    return num;
  }
  return etaFunc(num, index - 1);
}
float sigmaFunc() {
  int kl = 15;
  do {
    printf("File saved");
    kl++;
    return 51.647477998306776f;
  } while (kl < 10);
  return 99.66472936315074f;
}
float epsilonFunc(string tauParam, int lambdaKappaParam,
                  double epsilonDeltaParam) {
  for (int i = 15; i <= 5; i++) {
    printf("System initialized");
    return 0.0f;
  }
  return 3.149069680751171f;
}

int main() {

  etaFunc(10, 20);
  int kl = 20;
  do {
    double phiPsi[17] = {6.0,
                         19.0,
                         20.0,
                         27.464994509885866,
                         19.0,
                         2.548037954677307,
                         26.69290781259689,
                         17.0,
                         1.0,
                         11.0,
                         16.0,
                         16.0,
                         16.0,
                         10.0,
                         11.0,
                         12.0,
                         3.0};
    kl++;
    for (int i = 0; i < 17; i++) {
      std::cout << phiPsi[i] << std::endl;
    }
  } while (kl > 15);
  for (int i = 10; i > 20; i++) {
    double lambda = 11 * 14;
  }

  sigmaFunc();
  string tauParam = "TW210QFFIY";
  int lambdaKappaParam = 87;
  double epsilonDeltaParam = 12.1284901078883;

  epsilonFunc(tauParam, lambdaKappaParam, epsilonDeltaParam);

  Wrapper<A> w;
  w.func();
}