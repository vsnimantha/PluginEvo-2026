#include <stdio.h>
#include <stdint.h>
#include <setjmp.h>

struct u_leaf {
    int a __attribute__((user));
    int b;
};

struct u_leaf2 {
    int x;
    int y __attribute__((user));
};

struct u_pair {
    struct u_leaf  l1;
    struct u_leaf2 l2;
    int tag;
};

struct u_mid {
    struct u_pair p1;
    struct u_pair p2;
    int flags __attribute__((user));
};

struct u_big {
    struct u_mid m1;
    struct u_mid m2;
    struct u_mid m3;
    int extra;
};

union u_union {
    struct u_leaf  leaf;
    struct u_leaf2 leaf2;
    int raw __attribute__((user));
};

struct u_array {
    int len;
    struct u_leaf elems[16];
};

struct non_u {
    long a;
    long b;
};

struct u_leaf  g_leaf;
struct u_mid   g_mid;
struct u_big   g_big;
union  u_union g_u;
struct u_array g_arr;
struct non_u   g_plain;

int f_many_structs(int seed)
{
    struct u_leaf  l1, l2, l3, l4, l5, l6, l7, l8;
    struct u_mid   m1, m2, m3, m4;
    struct u_big   b1, b2;
    union  u_union u1, u2;
    struct non_u   n1, n2;

    l1.a = seed;     l2.a = seed+1; l3.a = seed+2; l4.a = seed+3;
    l5.a = seed+4;   l6.a = seed+5; l7.a = seed+6; l8.a = seed+7;

    m1.flags = seed+8;  m2.flags = seed+9;
    m3.flags = seed+10; m4.flags = seed+11;

    b1.m1.flags = seed+12;
    b2.m2.flags = seed+13;

    u1.raw = seed+14;
    u2.raw = seed+15;

    n1.a = seed+16;
    n2.a = seed+17;

    return l1.a + l2.a + l3.a + l4.a + l5.a + l6.a + l7.a + l8.a +
           m1.flags + m2.flags + m3.flags + m4.flags +
           b1.m1.flags + b2.m2.flags +
           u1.raw + u2.raw +
           (int)n1.a + (int)n2.a;
}

int f_byref_stress(int base)
{
    struct u_leaf  l[16];
    struct u_mid   m[8];
    struct u_big   b[4];
    struct non_u   n[8];

    struct u_leaf  *pl[16];
    struct u_mid   *pm[8];
    struct u_big   *pb[4];
    struct non_u   *pn[8];

    for (int i = 0; i < 16; ++i) pl[i] = &l[i];
    for (int i = 0; i < 8; ++i)  pm[i] = &m[i];
    for (int i = 0; i < 4; ++i)  pb[i] = &b[i];
    for (int i = 0; i < 8; ++i)  pn[i] = &n[i];

    int sum = 0;
    for (int i = 0; i < 16; ++i) {
        pl[i]->a = base + i;
        sum += pl[i]->a;
    }
    for (int i = 0; i < 8; ++i) {
        pm[i]->flags = base + 100 + i;
        sum += pm[i]->flags;
    }
    for (int i = 0; i < 4; ++i) {
        pb[i]->m1.flags = base + 200 + i;
        sum += pb[i]->m1.flags;
    }
    for (int i = 0; i < 8; ++i) {
        pn[i]->a = base + 300 + i;
        sum += (int)pn[i]->a;
    }

    return sum;
}

int f_array_stress(int base)
{
    struct u_leaf arr1[64];
    struct u_pair arr2[32];
    struct u_mid  arr3[16];

    for (int i = 0; i < 64; ++i) {
        arr1[i].a = base + i;
        arr1[i].b = base - i;
    }
    for (int i = 0; i < 32; ++i) {
        arr2[i].l1.a = base + i * 2;
        arr2[i].l2.y = base + i * 3;
    }
    for (int i = 0; i < 16; ++i) {
        arr3[i].flags = base + i * 5;
    }

    int sum = 0;
    for (int i = 0; i < 64; ++i)
        sum += arr1[i].a + arr1[i].b;
    for (int i = 0; i < 32; ++i)
        sum += arr2[i].l1.a + arr2[i].l2.y;
    for (int i = 0; i < 16; ++i)
        sum += arr3[i].flags;

    return sum;
}

int f_cfg_stress(int x)
{
    struct u_leaf a, b;
    struct u_mid  m;
    struct non_u  n;
    int sum = 0;

    for (int i = 0; i < 50; ++i) {
        if (i & 1) {
            a.a = x + i;
            sum += a.a;
        } else {
            b.a = x - i;
            sum += b.a;
        }

        switch (i % 5) {
        case 0:
            m.flags = i;
            sum += m.flags;
            break;
        case 1:
            n.a = i * 2;
            sum += (int)n.a;
            break;
        case 2:
            if (i > 20)
                goto L1;
            sum += i * 3;
            break;
        case 3:
            sum += i * 4;
            break;
        case 4:
            sum += i * 5;
            break;
        }
    }

L1:
    return sum;
}

int f_jmp_stress(int x)
{
    struct u_leaf l1, l2;
    jmp_buf jb;
    int res = 0;

    if (setjmp(jb) == 0) {
        l1.a = x + 10;
        res += l1.a;
        if (x & 1)
            longjmp(jb, 1);
        l2.a = x + 20;
        res += l2.a;
        return res;
    } else {
        l1.a = x + 30;
        l2.a = x + 40;
        return l1.a + l2.a;
    }
}

int f_mass_locals(int seed)
{
    struct u_leaf  L[32];
    struct u_mid   M[16];
    struct u_big   B[8];
    struct non_u   N[16];

    int sum = 0;
    for (int i = 0; i < 32; ++i) {
        L[i].a = seed + i;
        sum += L[i].a;
    }
    for (int i = 0; i < 16; ++i) {
        M[i].flags = seed + 100 + i;
        sum += M[i].flags;
    }
    for (int i = 0; i < 8; ++i) {
        B[i].m1.flags = seed + 200 + i;
        B[i].m2.flags = seed + 300 + i;
        sum += B[i].m1.flags + B[i].m2.flags;
    }
    for (int i = 0; i < 16; ++i) {
        N[i].a = seed + 400 + i;
        sum += (int)N[i].a;
    }
    return sum;
}

int f_small1(int x) { struct u_leaf l; l.a = x; return l.a + 1; }
int f_small2(int x) { struct u_leaf l; l.a = x+1; return l.a + 2; }
int f_small3(int x) { struct u_leaf l; l.a = x+2; return l.a + 3; }
int f_small4(int x) { struct u_leaf l; l.a = x+3; return l.a + 4; }
int f_small5(int x) { struct u_leaf l; l.a = x+4; return l.a + 5; }
int f_small6(int x) { struct u_leaf l; l.a = x+5; return l.a + 6; }
int f_small7(int x) { struct u_leaf l; l.a = x+6; return l.a + 7; }
int f_small8(int x) { struct u_leaf l; l.a = x+7; return l.a + 8; }

int f_no_userspace(int x)
{
    struct non_u a, b;
    a.a = x;
    a.b = x+1;
    b.a = x+2;
    b.b = x+3;
    return (int)(a.a + a.b + b.a + b.b);
}

int main(void)
{
    int r = 0;
    r += f_many_structs(10);
    r += f_byref_stress(20);
    r += f_array_stress(30);
    r += f_cfg_stress(40);
    r += f_jmp_stress(50);
    r += f_mass_locals(60);
    r += f_small1(1) + f_small2(2) + f_small3(3) + f_small4(4);
    r += f_small5(5) + f_small6(6) + f_small7(7) + f_small8(8);
    r += f_no_userspace(99);

    printf("result = %d\n", r);
    return 0;
}
