#include <cstring>
#include <new>

struct Complex { int data[100]; Complex* ptr; };

__attribute__((noinline, optimize("O0")))
void ultimate_nuke() {
    Complex* c = new Complex[10]; 
    c[0].ptr = new Complex;
    
    char arr1[4096], arr2[4096];
    memset(arr1, 0xAA, 4096);
    memcpy(arr2, arr1, 4096);
    
    int s0=0,s1=s0+1,s2=s1*2,s3=s2/3,s4=s3%5,s5=s4^s0;
    
    for(int i=0; i<2000; i++) {
        int t=i*i; 
        if(t%7==0) s5+=t; 
        else s5*=2;
    }
}

int main() {
    ultimate_nuke();
    return 0;
}
