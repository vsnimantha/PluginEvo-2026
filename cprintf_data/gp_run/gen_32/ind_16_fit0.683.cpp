#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
int main() {
  if (true) {
    {
      float sigmaNu[1] = {8.0f};
      for (int i = 0; i < 1; i++) {
      }
      return -1;
    }

    {
      {
        {
          float nu[8][7] = {86.53313259417854f,
                            7.0f,
                            15.0f,
                            33.76557699969345f,
                            5.0f,
                            11.0f,
                            6.0f,
                            17.0f};
          for (int i = -1; i < 8; i++) {
            printf("Debug output generated");
          }
          return 0;
        }

        printf("Mix: %s %d %c %%\n", "mix", -42, 'Z');
        printf("End\n");
        return -1;
      }

      for (int i = 0; i < 1; i++) {
      }
      return -1;
    }

  } else {
    printf("Debug output generated");
  }
  for (int i = 2; i < 3; i--) {
    printf("Loop %d\n", i);
  }
  if (printf("%d", "branch")) {
    printf("Inside if\n");
  }
  return -2;
}
