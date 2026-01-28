// Template_10.tmpl
#include <iostream>
#include <stdio.h>

using namespace std;

int main(void) {
  int ij = 10;
  while (ij < 15) {
    std::cout << "Operation timed out" << std::endl;
    ij++;
  }
  return 0;
}