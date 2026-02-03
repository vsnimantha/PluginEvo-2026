#include <stdio.h>

#define __randomize_layout __attribute__((randomize_layout))

struct __randomize_layout Ops3 {
    int (*f1)(int);
    int (*f2)(int);
};

struct __randomize_layout Ops2 {
    struct Ops3 *nested;
    int (*g1)(int, int);
};

struct __randomize_layout Ops1 {
    struct Ops2 inner;
    int (*h1)(const char *);
};

struct __randomize_layout DeepNested {
    int a;
    struct Ops1 lvl1;
    struct __randomize_layout Inner {
        struct Ops2 *ptr;
        long long arr[3];
        struct Ops3 inline_ops;
    } inner;
    char *name;
};

static int id(int x) { return x; }
static int add(int a, int b) { return a + b; }
static int len(const char *s) {
    int n = 0;
    while (s && *s++) n++;
    return n;
}

int main(void)
{
    struct DeepNested obj = {
        .a = 1,
        .lvl1 = {
            .inner = {
                .nested = NULL,
                .g1 = add,
            },
            .h1 = len,
        },
        .inner = {
            .ptr = NULL,
            .arr = {1, 2, 3},
            .inline_ops = { id, id },
        },
        .name = "test",
    };

    int v = obj.lvl1.h1(obj.name);
    printf("a=%d len(name)=%d arr0=%lld\n", obj.a, v, obj.inner.arr[0]);
    return 0;
}
