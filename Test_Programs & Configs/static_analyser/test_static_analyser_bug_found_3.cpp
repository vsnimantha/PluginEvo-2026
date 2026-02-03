__attribute__((noinline, optimize("O0")))
void stmt_overload() {
    int total = 0;
    
    for(int i = 0; i < 5000; i++) {
        int t1 = i * i;
        int t2 = i + t1;
        int t3 = t2 * 2;
        int t4 = t3 / 3;
        int t5 = t4 % 5;
        
        if(t1 % 3 == 0) total += t1;
        else if(t2 % 5 == 0) total -= t2;
        else total = total ^ i;
    }
}

int main() {
    stmt_overload();
    return 0;
}
