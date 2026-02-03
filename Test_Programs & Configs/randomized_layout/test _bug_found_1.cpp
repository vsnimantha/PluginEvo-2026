#include <stdio.h>
#include <setjmp.h>

#define __latent_entropy __attribute__((latent_entropy))

volatile unsigned long latent_entropy __latent_entropy;

static jmp_buf jb1;
static jmp_buf jb2;

int __latent_entropy f_leaf(int x)
{
    if (x < 0)
        return -1;
    if (x == 0)
        return 0;
    if (x & 1)
        return x * 2;
    return x / 2;
}

void __latent_entropy f_jump(int n)
{
    int r1 = setjmp(jb1);
    int r2 = setjmp(jb2);

    if (r1 == 0 && r2 == 0) {
        for (int i = 0; i < n; ++i) {
            if (i == 1)
                longjmp(jb1, 1);
            if (i == 2)
                goto out1;
            if (i == 3)
                longjmp(jb2, 2);
        }
    } else if (r1 == 1) {
        goto out2;
    } else if (r2 == 2) {
        return;
    } else {
        goto out1;
    }

out1:
    printf("out1: n=%d r1=%d r2=%d\n", n, r1, r2);
    return;

out2:
    printf("out2: n=%d r1=%d r2=%d\n", n, r1, r2);
}

int __latent_entropy f_chain(int n)
{
    int sum = 0;

    for (int i = -2; i <= n; ++i) {
        int v = f_leaf(i);
        if (v < 0)
            continue;
        if (v == 0 && i != 0)
            return v;
        sum += v;
    }

    if (sum > 1000)
        return sum - 1000;

    return sum;
}

int __latent_entropy f_mixed(int n)
{
    int res = 0;

    if (n < 0)
        goto neg_case;

    f_jump(n);

    for (int i = 0; i < n; ++i) {
        res += f_chain(i);
        if ((res & 1) && i > 3)
            goto done;
    }

done:
    return res;

neg_case:
    f_jump(-n);
    return -f_chain(-n);
}

int main(int argc, char **argv)
{
    int a = f_leaf(argc - 2);
    f_jump(argc);
    int b = f_chain(argc);
    int c = f_mixed(argc - 1);

    printf("a=%d b=%d c=%d\n", a, b, c);
    return (a ^ b ^ c) & 0xff;
}
