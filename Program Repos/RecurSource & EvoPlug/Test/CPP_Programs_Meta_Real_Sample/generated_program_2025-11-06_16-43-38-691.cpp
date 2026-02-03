// Template_12.tmpl
#include <cstdio>
#include <iostream>
using namespace std;

int main() {
  int kl = 15;
  do {
    double xiLambda = 11 / 9;
    kl++;
  } while (kl > 10);
  for (int i = 20; i <= 5; i++) {
    float betaNu[3] = {18.0f, 10.0f, 16.0f};
    for (int i = 0; i < 3; i++) {
      std::cout << betaNu[i] << std::endl;
    }
  }
  int piOmega[9] = {13, 12, 20, 17, 18, 4, 19, 20, 20};
  for (int i = 0; i < 9; i++) {
    std::cout << piOmega[i] << std::endl;
  }
  return 0;
}