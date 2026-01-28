#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
int main() {
  {
    printf("Hello %s %d %c\n", "world", 42, '!');
    return 0;
  }

  printf("Mix: %s %d %c %%\n", "mix", -42, 'Z');
  printf("End\n");
  return printf("Float: %f\n", 3.14);
}
