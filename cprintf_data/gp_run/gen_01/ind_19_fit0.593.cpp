#include <cstdio>
#include <iostream>
#include <stdlib.h>
#include <thread>
using namespace std;
int x = 0;
void inc() {
  for (int i = 0; i < 1000; ++i)
    ++x;
}
int lambdaFunc(int num, int index) {
  for (int i = 0; i < 0; i++) {
    double nu = 6 * 10;
  }
  if (index >= 5) {
    return num;
  }
  return lambdaFunc(num, index - 1);
}
void lambdaFunc() { double omegaTau = 12 + 4; }
int lambdaFunc(int thetaKappaParam) {
  string eta[16] = {"CrystalCascade", "CelestialJourney", "9ZGV55LA6Z",
                    "GoldenPhoenix",  "MajesticWhisper",  "AzureFlame",
                    "InfiniteDreams", "EtherealGlow",     "AzureFlame",
                    "RadiantEcho",    "V2E0CU3FD9",       "MajesticWhisper",
                    "CrystalCascade", "AzureFlame",       "GoldenPhoenix",
                    "RadiantEcho"};
  for (int i = 0; i < 16; i++) {
    std ::cout << eta[i] << std ::endl;
  }
  return 0;
}
int main() {
  lambdaFunc(10, 20);
  int kl = 15;
  do {
    printf("MHLUIJAOAA6YWE1CI8FG");
    kl++;
  } while (kl <= 5);
  for (int i = 5; i >= 10; i++) {
    bool chi[9] = {false, true, false, true, true, false, true, false, true};
    for (int i = 0; i < 9; i++) {
      std ::cout << chi[i] << std ::endl;
    }
  }
  lambdaFunc();
  int thetaKappaParam = 3;
  lambdaFunc(thetaKappaParam);
  std::thread t1(inc), t2(inc);
  t1.join();
  t2.join();
  std ::cout << x << "\n";
}
