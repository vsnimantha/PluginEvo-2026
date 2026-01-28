// Template_27.tmpl
#include <cstdio>
#include <iostream>
#include <stdlib.h>
using namespace std;

int iotaFunc(int num, int index) {
  for (int i = 5; i <= 20; i++) {
    bool muTheta[14] = {true, false, false, false, true,  true,  true,
                        true, true,  true,  false, false, false, false};
    for (int i = 0; i < 14; i++) {
      std::cout << muTheta[i] << std::endl;
    }
  }
  if (index >= 5) {
    return num;
  }
  return iotaFunc(num, index - 1);
}
float iotaFunc() {
  while (false) {
    double upsilonGamma[9] = {10.0, 1.0, 18.0, 4.0, 3.0, 15.0, 8.0, 18.0, 17.0};
    for (int i = 0; i < 9; i++) {
      std::cout << upsilonGamma[i] << std::endl;
    }
    return 91.16516609081587f;
  }
  return 0.0f;
}
void epsilonFunc(float psiDeltaParam) { string etaPhi = "2EQH24XCKQ"; }

int main() {

  iotaFunc(10, 20);
  int kl = 15;
  do {
    double kappa[14] = {6.0, 4.0, 2.0, 8.0, 11.0, 20.0, 19.0,
                        3.0, 2.0, 5.0, 6.0, 18.0, 9.0,  14.0};
    kl++;
    for (int i = 0; i < 14; i++) {
      std::cout << kappa[i] << std::endl;
    }
  } while (kl > 20);
  for (int i = 15; i > 20; i++) {
    float omegaSigma[10] = {2.0f,  20.0f, 9.0f,  20.0f, 3.0f,
                            12.0f, 10.0f, 20.0f, 14.0f, 17.0f};
    for (int i = 0; i < 10; i++) {
      std::cout << omegaSigma[i] << std::endl;
    }
  }

  iotaFunc();
  float psiDeltaParam = 10.422106520781805f;

  epsilonFunc(psiDeltaParam);

  int x = 2147483647; // INT_MAX
  int y = x + 1;      // Undefined behavior
  std::cout << y << "\n";
}
