// Template_25.tmpl

#include <iostream>
#include <stdlib.h>
using namespace std;

int iotaFunc(int num, int index) {
  std::cout << "This is a sample print statement" << std::endl;
  if (index >= 5) {
    return num;
  }
  return iotaFunc(num, index - 1);
}
double kappaFunc() {
  int lambda = 48;
  return 76.23334897342835;
}
void alphaFunc(float deltaPsiParam, bool omegaParam, double zetaParam) {
  int kl = 15;
  do {
    double phiPsi = 12 / 10;
    kl++;
  } while (kl < 10);
}

int main() {

  iotaFunc(10, 20);
  int kl = 5;
  do {
    int deltaEpsilon[8] = {15, 10, 8, 2, 9, 11, 2, 15};
    kl++;
    for (int i = 0; i < 8; i++) {
      std::cout << deltaEpsilon[i] << std::endl;
    }
  } while (kl < 5);
  for (int i = 15; i > 5; i++) {
    double etaIota[12] = {19.0, 9.0,  19.0, 14.0, 18.0, 17.0,
                          2.0,  10.0, 8.0,  16.0, 18.0, 20.0};
    for (int i = 0; i < 12; i++) {
      std::cout << etaIota[i] << std::endl;
    }
  }

  kappaFunc();
  float deltaPsiParam = 54.24033828489191f;
  bool omegaParam = true;
  double zetaParam = 83.87968034338475;

  alphaFunc(deltaPsiParam, omegaParam, zetaParam);

  return 0;
}
