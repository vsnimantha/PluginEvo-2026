#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

volatile int a = 1;
volatile int b = 2;

int side(int *p) {
    return (*p)++;
}

int main(void) {
    int x = a;
    int y = b;

    assert((side((int *)&x), x + y) == (x + y));

    return 0;
}
