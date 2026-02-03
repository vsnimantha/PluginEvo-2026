#include <iostream>
#include <setjmp.h>

jmp_buf env;

__attribute__((noinline, optimize("O0")))
void victim() {
    char buf[32];
    char shadow[8];
    
    longjmp(env, 1);
}

int main() {
    if (setjmp(env) == 0) {
        victim();
    }
    return 0;
}
