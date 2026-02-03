// Template_57.tmpl
#include <iostream>
#include <cstdio>

using namespace std;

int muFunc(int num, int index) {
  printf("CEUYK1OS543KBF4HRA6U");
  if (index >= 5) {
    return num;
  }
  return muFunc(num, index - 1);
}
int iotaFunc() {
  double etaIota[1] = {10.0};
  for (int i = 0; i < 1; i++) {
    std::cout << etaIota[i] << std::endl;
  }
  return 0;
}

int main() {

  muFunc(10, 20);
  int kl = 20;
  do {
    float gamma[20] = {
        3.0f,  7.0f,  18.0f, 14.0f, 9.0f,  8.0f,  19.0f,
        19.0f, 5.0f,  3.0f,  18.0f, 14.0f, 18.0f, 5.691889292614583f,
        16.0f, 17.0f, 8.0f,  9.0f,  16.0f, 9.0f};
    kl++;
    for (int i = 0; i < 20; i++) {
      std::cout << gamma[i] << std::endl;
    }
  } while (kl > 15);
  for (int i = 5; i < 5; i++) {
    double mu[19] = {13.0, 20.0,
                     18.0, 6.0,
                     9.0,  10.0,
                     16.0, 9.0,
                     7.0,  14.0,
                     18.0, 18.0,
                     12.0, 13.0,
                     4.0,  77.34591110312395,
                     4.0,  13.337681341669827,
                     9.0};
    for (int i = 0; i < 19; i++) {
      std::cout << mu[i] << std::endl;
    }
  }

  iotaFunc();

  int x = 1 / 0; // UB: integer divide by zero
  return x;
}