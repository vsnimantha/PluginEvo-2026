#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdint.h>
#include <limits.h>

// 1️⃣ Dangling Pointer (Undefined Behavior)
void test_dangling_pointer() {
    int *ptr = malloc(sizeof(int));
    *ptr = 42;
    free(ptr);  // Pointer is now dangling
    
    printf("Accessing freed memory: %d\n", *ptr);  // Undefined behavior!
}

// 2️⃣ Integer Overflow (Undefined Behavior)
void test_integer_overflow() {
    int x = INT_MAX;
    int y = x + 1;  // Undefined behavior
    printf("Overflowed value: %d\n", y);
}

// 3️⃣ Floating-Point Precision Issue
void test_floating_point_precision() {
    float a = 0.1f;
    float b = a * 10;
    
    if (b == 1.0f) {
        printf("Equal!\n");
    } else {
        printf("Not equal! (b = %.10f)\n", b);
    }
}

// 4️⃣ Strict Aliasing Rule Violation
void test_strict_aliasing() {
    int x = 42;
    float *ptr = (float*)&x;  // Violates strict aliasing
    printf("Aliased value: %f\n", *ptr);
}

// 5️⃣ Volatile Variable Optimization Issue
volatile int x = 0;
void test_volatile_behavior() {
    while (x == 0) {
        printf("Waiting...\n");
    }
    printf("Exited loop\n");
}

// 6️⃣ Stack Overflow (Infinite Recursion)
void test_stack_overflow(int depth) {
    printf("Depth: %d\n", depth);
    test_stack_overflow(depth + 1);  // Recursion with no base case
}

// 7️⃣ Buffer Overflow
void test_buffer_overflow() {
    char arr[5] = "test";
    arr[10] = 'X';  // Out-of-bounds write
    printf("Buffer overflow value: %c\n", arr[10]);  // Undefined behavior!
}

// 8️⃣ Uninitialized Variable
void test_uninitialized_variable() {
    int x;  // Uninitialized variable
    printf("Uninitialized value: %d\n", x);  // Could print garbage!
}

// 9️⃣ Memory Alignment & Misaligned Access
void test_misaligned_access() {
    uint32_t data = 0x12345678;
    uint8_t *ptr = (uint8_t*)&data;
    
    printf("Misaligned access: %x\n", *(uint32_t*)(ptr + 1));  // Might crash!
}

// 🔟 Race Condition in Multithreading
int counter = 0;

void* increment_counter(void* arg) {
    for (int i = 0; i < 100000; i++) {
        counter++;  // No synchronization!
    }
    return NULL;
}

void test_race_condition() {
    pthread_t t1, t2;
    pthread_create(&t1, NULL, increment_counter, NULL);
    pthread_create(&t2, NULL, increment_counter, NULL);
    
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    
    printf("Final counter value: %d\n", counter);  // Might be incorrect!
}

// 🚀 Main function to run tests
int main() {
    printf("Running C Compiler Test Cases...\n");

    test_dangling_pointer();
    test_integer_overflow();
    test_floating_point_precision();
    test_strict_aliasing();
    test_volatile_behavior();
    // test_stack_overflow(1); // Uncomment to test stack overflow (will likely crash)
    test_buffer_overflow();
    test_uninitialized_variable();
    test_misaligned_access();
    test_race_condition();

    return 0;
}
