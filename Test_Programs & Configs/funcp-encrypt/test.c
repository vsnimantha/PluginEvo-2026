typedef void (*fp)(void);

struct S {
    fp f;
};

void hello(void) {}

struct S make(int cond) {
    struct S s;
    if (cond)
        s.f = hello;
    else
        s.f = 0;
    return s;
}

int main() {
    struct S out = make(1);
    if (out.f)
        out.f();
    return 0;
}
