#include <stdio.h>
#define N 5

int maze[N][N] = {
    {1, 0, 1, 1, 1},
    {1, 1, 1, 0, 1},
    {0, 0, 1, 0, 1},
    {1, 1, 1, 1, 1},
    {0, 0, 0, 0, 1}
};

int solution[N][N];

int solveMaze(int x, int y) {
    if (x == N - 1 && y == N - 1) {
        solution[x][y] = 1;
        return 1;
    }

    if (x >= 0 && y >= 0 && x < N && y < N && maze[x][y] == 1) {
        if (solution[x][y] == 1)
            return 0;

        solution[x][y] = 1;

        if (solveMaze(x, y + 1)) return 1;
        if (solveMaze(x + 1, y)) return 1;
        if (solveMaze(x, y - 1)) return 1;
        if (solveMaze(x - 1, y)) return 1;

        solution[x][y] = 0; // Backtrack
    }
    return 0;
}

void printSolution() {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            printf("%d ", solution[i][j]);
        }
        printf("\n");
    }
}

int main() {
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            solution[i][j] = 0;

    if (solveMaze(0, 0))
        printSolution();
    else
        printf("No path found!\n");

    return 0;
}
