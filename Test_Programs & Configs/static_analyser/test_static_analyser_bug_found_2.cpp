#include <new>

struct Nested {
    int data[50];
    Nested* ptr1;
    Nested** ptr_array;
};

__attribute__((noinline, optimize("O0")))
void ptr_analyze() {
    Nested* base = new Nested[10];
    base[0].ptr1 = new Nested;
    base[0].ptr_array = new Nested*[5];
    base[0].ptr_array[0] = base[0].ptr1;
    base[0].ptr_array[1] = base;
    
    *base[0].ptr1->data = 42;
    *(base[0].ptr_array[0]->data) = 84;
    
    delete[] base[0].ptr_array;
    delete base[0].ptr1;
    delete[] base;
}

int main() {
    ptr_analyze();
    return 0;
}
