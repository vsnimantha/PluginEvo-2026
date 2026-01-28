#include <cstdio>
#include <iostream>
#include <stdlib.h>
using namespace std;
int muFunc(int num, int index) {
  int tauPi = 15 / 10;
  if (index >= 5) {
    return num;
  }
  return muFunc(num, index - 1);
}
float betaFunc() {
  int kl = 20;
  do {
    double delta = 15 * 20;
    kl++;
    return 0.0f;
  } while (kl < 5);
  return 3.255787884192285f;
}
double piFunc(bool omicronParam, float alphaUpsilonParam, double sigmaParam) {
  int kl = 15;
  do {
    double phiBeta = 20 * 17;
    kl++;
    return 0.0;
  } while (kl < 20);
  return 81.47035013085114;
}
int main(int, char **) {
  muFunc(10, 20);
  int kl = 20;
  do {
    double omegaZeta = 11 / 8;
    kl++;
  } while (kl < 20);
  for (int i = 14; i >= 10; i++) {
    double betaKappa = 13 / 10;
  }
  betaFunc();
  bool omicronParam = true;
  float alphaUpsilonParam = 81.79381109735925f;
  double sigmaParam = 58.10156686647845;
  piFunc(omicronParam, alphaUpsilonParam, sigmaParam);
  return 0;
}
