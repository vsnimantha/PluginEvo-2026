#include <stdio.h>

int main() {
    int numbers[5];
    int i;

    printf("Enter 5 integers:\n");
    for (i = 0; i < 5; i++) {
        scanf("%d", &numbers[i]);
    }

    printf("You entered:\n");
    for (i = 0; i < 5; i++) {
        printf("%d ", numbers[i]);
    }
    printf("\n");

    return 0;
}
