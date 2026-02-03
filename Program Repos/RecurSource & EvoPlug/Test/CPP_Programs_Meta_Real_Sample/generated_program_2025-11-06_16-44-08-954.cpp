// Template_24.tmpl
#include <iostream>
#include <stdlib.h>
using namespace std;

int betaFunc(int num, int index) {
  for (int i = 15; i >= 20; i++) {
    double eta[2] = {9.0, 4.0};
    for (int i = 0; i < 2; i++) {
      std::cout << eta[i] << std::endl;
    }
  }
  if (index >= 5) {
    return num;
  }
  return betaFunc(num, index - 1);
}
int etaFunc() {
  for (int i = 0; i < 10; i++) {
    double rhoUpsilon = 5 * 8;
    return 0;
  }
  return 0;
}
bool betaFunc(double alphaUpsilonParam, int chiParam, string deltaParam) {
  bool epsilonRho[5] = {false, false, true, true, false};
  for (int i = 0; i < 5; i++) {
    std::cout << epsilonRho[i] << std::endl;
  }
  return false;
}

int main(int, char **) {

  betaFunc(10, 20);
  int kl = 10;
  do {
    double muTheta = 11 * 16;
    kl++;
  } while (kl <= 20);
  for (int i = 5; i > 15; i++) {
    double chiTheta[11] = {9.0, 17.0, 4.0,  12.0, 17.0, 12.0,
                           6.0, 1.0,  16.0, 8.0,  20.0};
    for (int i = 0; i < 11; i++) {
      std::cout << chiTheta[i] << std::endl;
    }
  }

  etaFunc();
  double alphaUpsilonParam = 33.62068060593635;
  int chiParam = 28;
  string deltaParam = "TUOPVH7H66";

  betaFunc(alphaUpsilonParam, chiParam, deltaParam);

  return 0;
}
