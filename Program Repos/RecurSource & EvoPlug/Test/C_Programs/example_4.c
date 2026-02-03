#include <stdio.h>
#include <stdlib.h>

int main() {
    int n;
    printf("Enter an odd number for the magic square size: ");
    scanf("%d", &n);
    if (n % 2 == 0) {
        printf("Only odd numbers allowed!\n");
        return 1;
    }

    int magic[n][n];
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            magic[i][j] = 0;

    int num = 1, i = 0, j = n / 2;
    while (num <= n * n) {
        magic[i][j] = num++;
        int newi = (i - 1 + n) % n;
        int newj = (j + 1) % n;
        if (magic[newi][newj])
            i = (i + 1) % n;
        else {
            i = newi;
            j = newj;
        }
    }

    printf("Magic Square of size %d:\n", n);
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++)
            printf("%3d ", magic[i][j]);
        printf("\n");
    }

    return 0;
}
