#include <cstring>
#include <new>

__attribute__((noinline, optimize("O0")))
void ssa_hell() {
    int a = 1, b = 2, c = a + b;
    
    int* ptr = new int(c);
    *ptr = c * 2;
    int x = *ptr + a;
    
    int arr[100];
    for(int i = 0; i < 100; i++) {
        arr[i] = x + i;
    }
    
    delete ptr;
}

int main() {
    ssa_hell();
    return 0;
}
