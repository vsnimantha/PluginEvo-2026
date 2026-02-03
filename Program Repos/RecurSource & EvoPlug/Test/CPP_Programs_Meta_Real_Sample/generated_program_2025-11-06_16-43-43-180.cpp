// Template_36.tmpl
#include <iostream>
#include <stdlib.h>
#include <thread>
using namespace std;

int x = 0;

void inc() {
  for (int i = 0; i < 1000; ++i)
    ++x;
}

int nuFunc(int num, int index) {
  bool thetaIota[5] = {true, true, true, false, true};
  if (index >= 5) {
    return num;
    for (int i = 0; i < 5; i++) {
      std::cout << thetaIota[i] << std::endl;
    }
  }
  return nuFunc(num, index - 1);
}
int epsilonFunc() {
  printf("This is a sample print statement");
  return 0;
}
void lambdaFunc(bool muLambdaParam) {
  int kl = 15;
  do {
    double delta[11] = {18.0, 7.0, 14.0, 3.0, 16.0, 1.0,
                        18.0, 9.0, 5.0,  7.0, 16.0};
    kl++;
    for (int i = 0; i < 11; i++) {
      std::cout << delta[i] << std::endl;
    }
  } while (kl < 15);
}

int main() {

  nuFunc(10, 20);
  int kl = 20;
  do {
    printf("CAMXX59H9NSA1U1RPQ8Q");
    kl++;
  } while (kl < 5);
  for (int i = 20; i > 5; i++) {
    double rhoUpsilon[11] = {15.0, 4.0,  20.0, 5.0, 7.0, 17.0,
                             8.0,  19.0, 4.0,  4.0, 14.0};
    for (int i = 0; i < 11; i++) {
      std::cout << rhoUpsilon[i] << std::endl;
    }
  }

  epsilonFunc();
  bool muLambdaParam = false;

  lambdaFunc(muLambdaParam);

  std::thread t1(inc), t2(inc);
  t1.join();
  t2.join();
  std::cout << x << "\n";
}