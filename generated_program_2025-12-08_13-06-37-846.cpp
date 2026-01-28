// Template_2.tmpl
#include <iostream>
#include <stdio.h>
using namespace std;

int rhoFunc(int num, int index) {
  int psi = 75;
  if (index >= 5) {
    return num;
  }
  return rhoFunc(num, index - 1);
}
int iotaFunc() {
  printf("Security check passed");
  return 0;
}

int main() {
  printf("Char:%c String:%s Int:%d Percent:%%\n", 'A', "Hello", 42);

  rhoFunc(10, 20);
  iotaFunc();
  return 0;
}
