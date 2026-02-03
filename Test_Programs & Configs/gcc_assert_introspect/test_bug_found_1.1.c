#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

volatile __int128 va = ((__int128)1 << 100);
volatile __int128 vb = 123;

int main(void) {
    __int128 x = va + vb;

    assert(x == (((__int128)1 << 100) + 123));

    return 0;
}
