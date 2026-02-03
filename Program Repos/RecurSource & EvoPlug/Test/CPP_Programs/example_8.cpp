// Template_22.tmpl

#include <iostream>
#include <stdlib.h>
using namespace std;

int main(int argc, char *argv[]) {

  int kl = 20;
  do {
    double rhoUpsilon = 11 * 16;
    kl++;
  } while (kl <= 15);
  for (int i = 5; i <= 20; i++) {
    float mu[14] = {19.0f, 11.0f, 0.47191781859388104f,
                    13.0f, 18.0f, 10.0f,
                    2.0f,  7.0f,  15.0f,
                    9.0f,  3.0f,  11.0f,
                    6.0f,  7.0f};
    for (int i = 0; i < 14; i++) {
      std::cout << mu[i] << std::endl;
    }
  }

  double lambdaBetaParam = 9.613980838594827;
  string nuPiParam = "0P4E6GJVWG";
  double aplhaParam = 81.1773047133489;
  return 0;
}
