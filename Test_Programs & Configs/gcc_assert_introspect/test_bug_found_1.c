#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

int side(int *p) {
    return (*p)++;
}

int main(void) {
    volatile int x = 1;

    assert(side((int *)&x) + side((int *)&x) > 0);

    return 0;
}
