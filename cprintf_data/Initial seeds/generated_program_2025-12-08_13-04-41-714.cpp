// Template_39.tmpl
#include <cstdio>
#include <iostream>
#include <stdlib.h>
using namespace std;

int tauFunc(int num, int index) {
  double omicron = 10 / 17;
  if (index >= 5) {
    return num;
  }
  return tauFunc(num, index - 1);
}
bool kappaFunc() {
  for (int i = 5; i < 20; i++) {
    double deltaEpsilon = 17 / 13;
    return false;
  }
  return true;
}
float phiFunc(float epsilonDeltaParam, int alphaParam,
              string alphaEpsilonParam) {
  std::cout << "System initialized" << std::endl;
  return 12.280770229970607f;
}

int main() {

  tauFunc(10, 20);
  int kl = 20;
  do {
    bool xiRho[11] = {true, false, true, true,  true, false,
                      true, false, true, false, false};
    kl++;
    for (int i = 0; i < 11; i++) {
      std::cout << xiRho[i] << std::endl;
    }
  } while (kl <= 15);
  for (int i = 15; i > 20; i++) {
    double rhoLambda = 11 / 13;
  }

  kappaFunc();
  float epsilonDeltaParam = 70.9657699727083f;
  int alphaParam = 23;
  string alphaEpsilonParam = "HJY0E0A95A";

  phiFunc(epsilonDeltaParam, alphaParam, alphaEpsilonParam);

  int x = 42;
  auto f = [=]() mutable {
    x++;
    std::cout << x << "\n";
  };
  f();
  std::cout << x << "\n"; // Did original x change?
}