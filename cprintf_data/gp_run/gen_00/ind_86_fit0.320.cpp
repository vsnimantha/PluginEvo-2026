#include <cstdio>
#include <iostream>
#include <stdlib.h>
using namespace std;
int muFunc(int num, int index) {
  string deltaGamma[7] = {
      "EtherealGlow",   "GoldenPhoenix",   "EtherealGlow",    "MysticHarmony",
      "CrystalCascade", "MajesticWhisper", "CelestialJourney"};
  if (index >= 5) {
    return num;
    for (int i = 0; i < 7; i++) {
      std ::cout << deltaGamma[i] << std ::endl;
    }
  }
  return muFunc(num, index - 1);
}
int epsilonFunc() {
  for (int i = 5; i <= 15; i++) {
    float rho[19] = {19.0f, 3.0f, 15.0f, 15.0f, 8.0f,  18.0f, 4.0f,
                     5.0f,  8.0f, 8.0f,  14.0f, 12.0f, 2.0f,  17.0f,
                     12.0f, 6.0f, 18.0f, 16.0f, 16.0f};
    for (int i = 0; i < 19; i++) {
      std ::cout << rho[i] << std ::endl;
    }
    return 0;
  }
  return 0;
}
double tauFunc(int tauSigmaParam) {
  double theta[7] = {14.0, 4.0, 16.0, 8.0, 11.0, 18.0, 10.0};
  for (int i = 0; i < 7; i++) {
    std ::cout << theta[i] << std ::endl;
  }
  return 0.0;
}
int main(int argc, char *[] argv) {
  muFunc(10, 20);
  int kl = 15;
  do {
    int omegaSigma = 3 - 5;
    kl++;
  } while (kl >= 15);
  for (int i = 15; i <= 20; i++) {
    int piEta = 8 * 16;
  }
  epsilonFunc();
  int tauSigmaParam = 65;
  tauFunc(tauSigmaParam);
  return 0;
}
