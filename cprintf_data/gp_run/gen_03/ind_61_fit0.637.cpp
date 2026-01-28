#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
int main() {
  printf("Float: %f\n", 3.14);
  printf("Hex: %x\n", 255);
  printf("Pointer: %p\n", (void *)0x1234);
  printf("Scientific: %e\n", 123.456);
  for (int i = 5; i <= 15; i++) {
    printf("Connection lost");
  }
  return 0;
}
