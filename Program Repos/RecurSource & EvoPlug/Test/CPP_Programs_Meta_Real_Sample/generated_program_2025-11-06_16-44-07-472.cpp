// Template_15.tmpl
#include <cstdio>
#include <iostream>
using namespace std;

// Placeholders
float sigmaFunc() {
  std::cout << "Exiting function" << std::endl;
  return 0.0f;
}
void tauFunc(float rhoPiParam) { printf("This is a sample print statement"); }

int main(int, char **) {

  // Placeholders
  sigmaFunc();
  float rhoPiParam = 37.79935412875383f;

  tauFunc(rhoPiParam);
  int tau = 35;
  if (false) {
    double omegaZeta[18] = {
        57.73640535975366, 8.0,  13.0, 11.0, 12.0, 10.0, 11.0, 16.0, 13.0,
        48.63637591954383, 18.0, 2.0,  10.0, 9.0,  3.0,  9.0,  13.0, 19.0};
    for (int i = 0; i < 18; i++) {
      std::cout << omegaZeta[i] << std::endl;
    }
  } else {
    int piEta[17] = {15, 19, 15, 2, 15, 13, 14, 11, 10,
                     76, 13, 9,  9, 9,  7,  16, 18};
    for (int i = 0; i < 17; i++) {
      std::cout << piEta[i] << std::endl;
    }
  }
  double rho = 13 / 15;
  int ij = 15;
  while (ij <= 5) {
    double sigmaNu = 17 * 8;
    ij++;
  }
  std::cout << "Code execution started" << std::endl;
  std::cout << "Code execution started" << std::endl;

  return 0;
}