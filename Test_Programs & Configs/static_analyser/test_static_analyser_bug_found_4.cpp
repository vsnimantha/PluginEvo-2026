#include <cstring>

__attribute__((noinline, optimize("O0")))
void array_chaos() {
    char src[4096], dst[4096], temp[2048], overlap[1024];
    char buf1[512], buf2[1024], buf3[2048];
    
    memset(src, 0xAA, 4096);
    memcpy(dst, src, 4096);
    memcpy(temp, dst + 1024, 2048);
    memcpy(overlap, temp, 1024);
    memcpy(dst, overlap, 1024);
    memcpy(src, dst + 2048, 1024);
    memcpy(buf1, src + 512, 512);
    memcpy(buf2, buf1, 1024);
}

int main() {
    array_chaos();
    return 0;
}
