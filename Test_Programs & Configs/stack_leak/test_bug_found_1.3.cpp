#include <stdio.h>
#include <stdlib.h>

struct stress_struct {
    char data[4096];
    struct stress_struct *next;
    int padding[1024];
};

struct nested_stress {
    struct stress_struct s1, s2, s3;
    char padding[8192];
};

__attribute__((constructor)) void ctor_stress(void) {
    struct stress_struct s;
    (void)s;
}

__attribute__((destructor)) void dtor_stress(void) {
    struct nested_stress n;
    (void)n;
}

static inline void inline_heavy(void) {
    struct stress_struct s;
    s.data[0] = 1;
}

static void static_heavy(void) {
    inline_heavy();
    alloca(64);
}

__attribute__((weak)) void weak_stress(void) {
    alloca(128);
}

union massive_union {
    char buf1[16384];
    char buf2[32768];
    struct { char data[65536]; } huge;
};

int main(void) {
    printf("=== Stress Test #4: Type/cgraph ONLY ===\n");
    
    struct stress_struct s1;
    struct nested_stress s2;
    union massive_union u;
    
    static_heavy();
    weak_stress();
    
    printf("Test #4 complete - no GIMPLE pass\n");
    return 0;
}
