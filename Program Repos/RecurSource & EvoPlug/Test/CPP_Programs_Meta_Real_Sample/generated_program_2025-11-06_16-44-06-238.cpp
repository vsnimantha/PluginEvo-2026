// Template_38.tmpl
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

int upsilonFunc(int num, int index) {
  printf("Memory allocation complete");
  if (index >= 5) {
    return num;
  }
  return upsilonFunc(num, index - 1);
}
void sigmaFunc() {
  for (int i = 5; i > 15; i++) {
    printf("This is a print statement");
  }
}
double omicronFunc(float betaPrimeParam, int deltaGammaParam,
                   double omegaParam) {
  std::cout << "Calculation finished" << std::endl;
  return 25.86406618478645;
}

int main() {

  upsilonFunc(10, 20);
  int kl = 15;
  do {
    printf("UZVZA2JW55C4P4WA4LCR");
    kl++;
  } while (kl < 5);
  for (int i = 20; i > 10; i++) {
    printf("EKOYYP98GD53ZJORDKEV");
  }

  sigmaFunc();
  float betaPrimeParam = 26.548689834551674f;
  int deltaGammaParam = 13;
  double omegaParam = 65.22323164496366;

  omicronFunc(betaPrimeParam, deltaGammaParam, omegaParam);

  MostDerived md;
  std::cout << sizeof(md) << "\n";
}