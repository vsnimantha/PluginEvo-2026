#include <stdio.h>

struct level1 { char pad[64]; struct level2 *next; };
struct level2 { char pad[64]; struct level3 *next; };
struct level3 { char pad[64]; struct level4 *next; };
struct level4 { char pad[64]; struct level5 *next; };
struct level5 { char pad[64]; struct level6 *next; };
struct level6 { char pad[64]; struct level7 *next; };
struct level7 { char pad[64]; struct level8 *next; };
struct level8 { char pad[64]; struct level9 *next; };
struct level9 { char pad[64]; struct level10 *next; };

typedef char massive_array_t[65536][1024];
typedef char nested_array_t[256][256][16];

struct bitfield_stress {
    unsigned int bf1 : 1;
    unsigned int bf2 : 2;
    unsigned int bf3 : 30;
    char padding[4096];
};

union type_confusion {
    struct { char buf[32768]; } a;
    struct { long long data[4096]; } b;
    char raw[65536];
};

struct forward_loop1;
struct forward_loop2;
struct forward_loop1 { struct forward_loop2 *ptr; };
struct forward_loop2 { struct forward_loop1 *ptr; };

extern void pure_type_stress(void);
extern int global_var;

int main(void) {
    printf("=== Stress Test #5: PURE TYPES ===\n");
    
    struct level1 s1;
    massive_array_t arr1;
    union type_confusion u;
    
    printf("Type stress complete\n");
    return 0;
}
