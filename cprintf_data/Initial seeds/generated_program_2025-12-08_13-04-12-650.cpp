// Template_17.tmpl
#include <cstdio>
#include <iostream>

using namespace std;

// Function definitions
float sigmaFunc() {
  std::cout << "Memory allocation complete" << std::endl;
  return 17.60885989188241f;
}
void upsilonFunc() {
  float xiLambda[11] = {9.0f,  15.0f, 17.0f, 7.0f,  13.0f, 10.0f,
                        19.0f, 14.0f, 19.0f, 18.0f, 6.0f};
  for (int i = 0; i < 11; i++) {
    std::cout << xiLambda[i] << std::endl;
  }
}

int main() {

  sigmaFunc();
  upsilonFunc();
  double xiLambda = 85.51858351717937;
  if (false) {
    float mu = 31.348551669267653f;
  } else {
    double pi[16] = {14.0, 2.0,  9.0,  2.0,  13.0, 87.9925743313971,
                     9.0,  16.0, 20.0, 18.0, 15.0, 18.0,
                     11.0, 11.0, 7.0,  2.0};
    for (int i = 0; i < 16; i++) {
      std::cout << pi[i] << std::endl;
    }
  }

  return 0;
}
