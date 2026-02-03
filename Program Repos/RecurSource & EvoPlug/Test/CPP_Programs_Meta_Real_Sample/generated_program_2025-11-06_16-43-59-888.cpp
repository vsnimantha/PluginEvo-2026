// Template_26.tmpl
#include <iostream>
#include <stdlib.h>
using namespace std;

int tauFunc(int num, int index) {
  for (int i = 20; i < 10; i++) {
    printf("Entering main loop");
  }
  if (index >= 5) {
    return num;
  }
  return tauFunc(num, index - 1);
}
bool piFunc() {
  std::cout << "Entering main loop" << std::endl;
  return true;
}
float tauFunc(string piParam, double betaParam, float nuParam) {
  double lambda = 13 / 12;
  return 0.0f;
}

int main() {

  tauFunc(10, 20);
  int kl = 10;
  do {
    double nuPhi = 16 / 8;
    kl++;
  } while (kl < 20);
  for (int i = 20; i < 15; i++) {
    int lambdaPi[18] = {3,  8,  2,  94, 3, 2,  11, 6, 3,
                        10, 17, 12, 6,  2, 13, 10, 4, 12};
    for (int i = 0; i < 18; i++) {
      std::cout << lambdaPi[i] << std::endl;
    }
  }

  piFunc();
  string piParam = "JLEGOJKS4C";
  double betaParam = 20.209875632652462;
  float nuParam = 28.71153311647342f;

  tauFunc(piParam, betaParam, nuParam);

  return 0;
}
