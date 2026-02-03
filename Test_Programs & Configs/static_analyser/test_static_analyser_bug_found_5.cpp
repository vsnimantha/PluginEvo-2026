__attribute__((noinline, optimize("O0")))
void ssa_explosion() {
    int a0=0, a1=a0+1, a2=a1*2, a3=a2/3, a4=a3%5, a5=a4^a0;
    int b0=a5+1, b1=b0*3, b2=b1/2, b3=b2%7, b4=b3^b0, b5=b4+10;
    int c0=b5*a0, c1=c0/4, c2=c1%11, c3=c2^c0, c4=c3+20, c5=c4*b5;
    int result = a5 + b5 + c5;
}

int main() {
    ssa_explosion();
    return 0;
}
