#include <stdio.h>
#include <stdint.h>
#include <string.h>

struct plain {
    int a;
    int b;
};

struct user_leaf {
    int u1 __attribute__((user));
    int u2;
};

struct user_nested_inner {
    int x;
    int y __attribute__((user));
};

struct user_nested_outer {
    struct user_nested_inner inner;
    int z;
};

union user_union {
    int  a __attribute__((user));
    long b;
};

struct mixed {
    struct plain        p;
    struct user_leaf    leaf;
    union  user_union   u;
    int                 tag;
};

struct no_user_anywhere {
    long x;
    long y;
};

struct user_array {
    int  len;
    int  data[8] __attribute__((user));
};

struct deep1 {
    struct user_leaf leaf;
    int flags;
};

struct deep2 {
    struct deep1 d1;
    struct plain p;
};

struct user_leaf            g_leaf;
struct user_nested_outer    g_outer;
union  user_union           g_u;
struct mixed                g_mixed;
struct no_user_anywhere     g_plain;
struct user_array           g_arr;
struct deep2                g_deep;

int f_simple_userspace(int v)
{
    struct user_leaf l1;
    struct user_nested_outer l2;
    union  user_union u1;

    l1.u1 = v;
    l2.inner.y = v + 1;
    u1.a = v + 2;

    return l1.u1 + l2.inner.y + u1.a;
}

int f_mixed_locals(int v)
{
    struct plain p;
    struct user_leaf leaf;
    struct no_user_anywhere n;
    struct deep2 d2;

    p.a = v;
    leaf.u2 = v + 1;
    n.x = v + 2;
    d2.d1.leaf.u1 = v + 3;

    return p.a + leaf.u2 + n.x + d2.d1.leaf.u1;
}

int f_byref_locals(int v)
{
    struct user_leaf l1;
    struct plain     p1;
    struct deep2     d2;

    struct user_leaf *pl1 = &l1;
    struct plain     *pp1 = &p1;
    struct deep2     *pd2 = &d2;

    pl1->u1 = v;
    pp1->a  = v + 1;
    pd2->d1.leaf.u1 = v + 2;

    return pl1->u1 + pp1->a + pd2->d1.leaf.u1;
}

int f_array_userspace(int base)
{
    struct user_leaf arr[4];
    struct user_array ua;

    for (int i = 0; i < 4; ++i) {
        arr[i].u1 = base + i;
        arr[i].u2 = base + i * 2;
    }

    ua.len = 4;
    for (int i = 0; i < ua.len; ++i)
        ua.data[i] = base + i * 3;

    int sum = 0;
    for (int i = 0; i < 4; ++i)
        sum += arr[i].u1 + arr[i].u2;

    for (int i = 0; i < ua.len; ++i)
        sum += ua.data[i];

    return sum;
}

int f_param_byref_leaf(struct user_leaf *pl, int v)
{
    pl->u1 = v;
    pl->u2 = v + 1;
    return pl->u1 + pl->u2;
}

int f_param_byref_deep(struct deep2 *pd, int v)
{
    pd->d1.leaf.u1 = v;
    pd->d1.leaf.u2 = v + 2;
    pd->d1.flags   = v + 3;
    return pd->d1.leaf.u1 + pd->d1.leaf.u2 + pd->d1.flags;
}

int f_cfg_stress(int x)
{
    struct user_leaf a;
    struct user_leaf b;
    struct plain     p;

    int sum = 0;

    for (int i = 0; i < 10; ++i) {
        if (i & 1) {
            a.u1 = x + i;
            sum += a.u1;
        } else {
            b.u2 = x - i;
            sum += b.u2;
        }

        switch (i % 3) {
            case 0:
                p.a = i;
                sum += p.a;
                break;
            case 1:
                sum += i * 2;
                break;
            case 2:
                if (i > 5)
                    goto L1;
                sum += i * 3;
                break;
        }
    }

L1:
    return sum;
}

int f_union_userspace(int x)
{
    union user_union u;
    u.a = x;
    if (x & 1)
        u.a += 10;
    else
        u.b = u.a * 2;
    return (int)u.b;
}

int f_no_userspace(int x)
{
    struct plain p;
    struct no_user_anywhere n;

    p.a = x;
    p.b = x + 1;
    n.x = x + 2;
    n.y = x + 3;

    return p.a + p.b + (int)n.x + (int)n.y;
}

int main(void)
{
    struct user_leaf      tmp_leaf;
    struct deep2          tmp_deep;

    printf("f_simple_userspace = %d\n", f_simple_userspace(5));
    printf("f_mixed_locals     = %d\n", f_mixed_locals(7));
    printf("f_byref_locals     = %d\n", f_byref_locals(9));
    printf("f_array_userspace  = %d\n", f_array_userspace(3));

    printf("f_param_byref_leaf = %d\n",
           f_param_byref_leaf(&tmp_leaf, 11));
    printf("f_param_byref_deep = %d\n",
           f_param_byref_deep(&tmp_deep, 13));

    printf("f_cfg_stress       = %d\n", f_cfg_stress(4));
    printf("f_union_userspace  = %d\n", f_union_userspace(6));
    printf("f_no_userspace     = %d\n", f_no_userspace(8));

    return 0;
}
