// Template_22.tmpl

#include <iostream>
#include <stdlib.h>
using namespace std;

int chiFunc(int num, int index) {
  double piEta = 12 * 14;
  if (index >= 5) {
    return num;
  }
  return chiFunc(num, index - 1);
}
bool lambdaFunc() {
  std::cout << "Entering main loop" << std::endl;
  return false;
}
int tauFunc(string xiParam, int lambdaParam, bool phiChiParam) {
  float rhoPsi[6] = {7.0f, 11.0f, 1.0f, 6.0f, 6.0f, 18.0f};
  for (int i = 0; i < 6; i++) {
    std::cout << rhoPsi[i] << std::endl;
  }
  return 98;
}

int main(int argc, char *argv[]) {

  chiFunc(10, 20);
  int kl = 5;
  do {
    printf("Default output text");
    kl++;
  } while (kl < 15);
  for (int i = 5; i <= 15; i++) {
    bool chiXi[16] = {false, true, true, false, false, true, true,  true,
                      false, true, true, true,  false, true, false, false};
    for (int i = 0; i < 16; i++) {
      std::cout << chiXi[i] << std::endl;
    }
  }

  lambdaFunc();
  string xiParam = "8F1PBCGG61";
  int lambdaParam = 47;
  bool phiChiParam = false;

  tauFunc(xiParam, lambdaParam, phiChiParam);
  return 0;
}
