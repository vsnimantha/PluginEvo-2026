// Template_28.tmpl
#include <iostream>
#include <stdlib.h>
using namespace std;

template <typename T> struct Wrapper {
  void foo() { T::bar(); } // Dependent name
};

struct A {
  static void bar() {}
};

int zetaFunc(int num, int index) {
  double phi = 20 - 16;
  if (index >= 5) {
    return num;
  }
  return zetaFunc(num, index - 1);
}
float betaFunc() {
  for (int i = 20; i > 15; i++) {
    float lambdaSigma[12] = {7.0f, 11.0f, 16.0f, 18.0f, 19.0f, 12.0f,
                             5.0f, 18.0f, 18.0f, 5.0f,  6.0f,  15.0f};
    for (int i = 0; i < 12; i++) {
      std::cout << lambdaSigma[i] << std::endl;
    }
    return 89.61599523125219f;
  }
  return 0.0f;
}
int phiFunc(double tauParam) {
  for (int i = 5; i > 20; i++) {
    printf("YR2R305JB7IWR36EX73S");
    return 43;
  }
  return 0;
}

int main() {

  zetaFunc(10, 20);
  int kl = 0;
  do {
    printf("File saved");
    kl++;
  } while (kl <= 20);
  for (int i = 5; i <= 20; i++) {
    printf("Entering main loop");
  }

  betaFunc();
  double tauParam = 85.04103984294575;

  phiFunc(tauParam);

  Wrapper<A> w;
  w.foo();
}
