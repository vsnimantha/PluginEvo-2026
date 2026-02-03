// main_template.tmpl
#include <iostream>
// Additional includes

using namespace std;

// Function definitions
double etaFunc() {
  int kl = 0;
  do {
    float eta[13] = {11.0f,
                     1.0f,
                     6.0f,
                     4.0f,
                     10.0f,
                     11.0f,
                     15.0f,
                     18.0f,
                     13.0f,
                     15.0f,
                     79.84229745437976f,
                     14.0f,
                     19.0f};
    kl++;
    for (int i = 0; i < 13; i++) {
      std::cout << eta[i] << std::endl;
    }
    return 38.063100990164486;
  } while (kl > 10);
  return 0.0;
}

int main() {
  // Function calls
  etaFunc();

  return 0;
}
