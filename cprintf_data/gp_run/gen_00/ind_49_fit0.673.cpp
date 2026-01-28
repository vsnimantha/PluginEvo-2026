#include <cstdio>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
void putchar(char c) { fputc(c, stdout); }
void putstring(const char *s) { fputs(s, stdout); }
void putint(int i) { printf("%d", i); }
int main() {
  printf("Hello %s %d %c\n", "world", 42, '!');
  return 0;
}
