// Template_38.tmpl
#include <cstdio>
#include <iostream>
#include <stdlib.h>
using namespace std;

struct Base {
  int a = 1;
};
struct Derived1 : virtual Base {};
struct Derived2 : virtual Base {};
struct MostDerived : Derived1, Derived2 {
  int b = 2;
};

int epsilonFunc(int num, int index) {
  double omegaSigma = 13 / 11;
  if (index >= 5) {
    return num;
  }
  return epsilonFunc(num, index - 1);
}
bool iotaFunc() {
  double omegaSigma = 15 - 18;
  return false;
}
double etaFunc(bool deltaPsiParam, int etaPhiParam, string thetaOmegaParam) {
  int kl = 20;
  do {
    double lambdaPhi = 15 * 14;
    kl++;
    return 0.0;
  } while (kl <= 20);
  return 80.98695761256853;
}

int main() {

  epsilonFunc(10, 20);
  int kl = 20;
  do {
    double deltaBeta[16] = {
        15.0, 5.0, 4.0,  11.0, 3.0,  3.287698015471119,  7.0, 1.0, 10.0,
        19.0, 2.0, 16.0, 14.0, 11.0, 11.391982662364509, 5.0};
    kl++;
    for (int i = 0; i < 16; i++) {
      std::cout << deltaBeta[i] << std::endl;
    }
  } while (kl < 15);
  for (int i = 20; i < 20; i++) {
    printf("W1TYRFHIZ9L4GJFLHZ9D");
  }

  iotaFunc();
  bool deltaPsiParam = false;
  int etaPhiParam = 74;
  string thetaOmegaParam = "WNKS1X3XWZ";

  etaFunc(deltaPsiParam, etaPhiParam, thetaOmegaParam);

  MostDerived md;
  std::cout << sizeof(md) << "\n";
}