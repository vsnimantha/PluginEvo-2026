#include <stdio.h>
#include <string.h>

__attribute__((noinline))
void vulnerable_function(const char *input)
{
    char buffer[32];
    strcpy(buffer, input);

    printf("Buffer: %s\n", buffer);
}

int main(int argc, char **argv)
{
    const char *msg = argc > 1 ? argv[1] : "hello";
    vulnerable_function(msg);
    return 0;
}
