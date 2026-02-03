#include <iostream>
#include <cstring>
#include <stdexcept>

#define GEN_FUZZ(ID)                                                \
__attribute__((noinline))                                           \
void fuzz_##ID(const char* s, int depth)                            \
{                                                                   \
    char buf[(ID % 17 + 1) * 8];                                    \
    std::strcpy(buf, s);                                            \
                                                                    \
    char vla[(ID % 9) + depth + 5];                                 \
    std::strcpy(vla, "vla");                                        \
                                                                    \
    char* p = (char*)__builtin_alloca((ID % 6 + 1) * 12);           \
    std::strcpy(p, "alloca");                                       \
                                                                    \
    auto lam = [&](int x) {                                         \
        char local[(ID % 5 + 1) * 7];                               \
        std::strcpy(local, "lam");                                  \
        return x - 1;                                               \
    };                                                              \
                                                                    \
    switch (ID % 4) {                                               \
        case 0: std::strcpy(buf, "A");                              \
        case 1: std::strcpy(buf, "B");                              \
        case 2: std::strcpy(buf, "C");                              \
        case 3: std::strcpy(buf, "D");                              \
    }                                                               \
                                                                    \
    if (depth == 0) {                                               \
        if (ID % 3 == 0) throw std::runtime_error("Error");         \
        return;                                                     \
    }                                                               \
                                                                    \
    if (ID % 2 == 0)                                                \
        fuzz_##ID(s, lam(depth));                                   \
}

GEN_FUZZ(1)   GEN_FUZZ(2)   GEN_FUZZ(3)   GEN_FUZZ(4)   GEN_FUZZ(5)
GEN_FUZZ(6)   GEN_FUZZ(7)   GEN_FUZZ(8)   GEN_FUZZ(9)   GEN_FUZZ(10)
GEN_FUZZ(11)  GEN_FUZZ(12)  GEN_FUZZ(13)  GEN_FUZZ(14)  GEN_FUZZ(15)
GEN_FUZZ(16)  GEN_FUZZ(17)  GEN_FUZZ(18)  GEN_FUZZ(19)  GEN_FUZZ(20)
GEN_FUZZ(21)  GEN_FUZZ(22)  GEN_FUZZ(23)  GEN_FUZZ(24)  GEN_FUZZ(25)
GEN_FUZZ(26)  GEN_FUZZ(27)  GEN_FUZZ(28)  GEN_FUZZ(29)  GEN_FUZZ(30)
GEN_FUZZ(31)  GEN_FUZZ(32)  GEN_FUZZ(33)  GEN_FUZZ(34)  GEN_FUZZ(35)
GEN_FUZZ(36)  GEN_FUZZ(37)  GEN_FUZZ(38)  GEN_FUZZ(39)  GEN_FUZZ(40)
GEN_FUZZ(41)  GEN_FUZZ(42)  GEN_FUZZ(43)  GEN_FUZZ(44)  GEN_FUZZ(45)
GEN_FUZZ(46)  GEN_FUZZ(47)  GEN_FUZZ(48)  GEN_FUZZ(49)  GEN_FUZZ(50)
GEN_FUZZ(51)  GEN_FUZZ(52)  GEN_FUZZ(53)  GEN_FUZZ(54)  GEN_FUZZ(55)
GEN_FUZZ(56)  GEN_FUZZ(57)  GEN_FUZZ(58)  GEN_FUZZ(59)  GEN_FUZZ(60)
GEN_FUZZ(61)  GEN_FUZZ(62)  GEN_FUZZ(63)  GEN_FUZZ(64)  GEN_FUZZ(65)
GEN_FUZZ(66)  GEN_FUZZ(67)  GEN_FUZZ(68)  GEN_FUZZ(69)  GEN_FUZZ(70)
GEN_FUZZ(71)  GEN_FUZZ(72)  GEN_FUZZ(73)  GEN_FUZZ(74)  GEN_FUZZ(75)
GEN_FUZZ(76)  GEN_FUZZ(77)  GEN_FUZZ(78)  GEN_FUZZ(79)  GEN_FUZZ(80)
GEN_FUZZ(81)  GEN_FUZZ(82)  GEN_FUZZ(83)  GEN_FUZZ(84)  GEN_FUZZ(85)
GEN_FUZZ(86)  GEN_FUZZ(87)  GEN_FUZZ(88)  GEN_FUZZ(89)  GEN_FUZZ(90)
GEN_FUZZ(91)  GEN_FUZZ(92)  GEN_FUZZ(93)  GEN_FUZZ(94)  GEN_FUZZ(95)
GEN_FUZZ(96)  GEN_FUZZ(97)  GEN_FUZZ(98)  GEN_FUZZ(99)  GEN_FUZZ(100)

extern "C" void __stack_chk_guard() {}

__attribute__((noinline))
void force_symbol()
{
    asm volatile(
        "lea __stack_chk_guard(%%rip), %%rax\n"
        :
        :
        : "rax"
    );
}

int main()
{
    force_symbol();

    const char* msg = "fuzz";

    for (int i = 1; i <= 100; i++) {
        try {
            switch (i) {
                #define CALL(ID) case ID: fuzz_##ID(msg, 3); break;
                CALL(1) CALL(2) CALL(3) CALL(4) CALL(5)
                CALL(6) CALL(7) CALL(8) CALL(9) CALL(10)
                CALL(11) CALL(12) CALL(13) CALL(14) CALL(15)
                CALL(16) CALL(17) CALL(18) CALL(19) CALL(20)
                CALL(21) CALL(22) CALL(23) CALL(24) CALL(25)
                CALL(26) CALL(27) CALL(28) CALL(29) CALL(30)
                CALL(31) CALL(32) CALL(33) CALL(34) CALL(35)
                CALL(36) CALL(37) CALL(38) CALL(39) CALL(40)
                CALL(41) CALL(42) CALL(43) CALL(44) CALL(45)
                CALL(46) CALL(47) CALL(48) CALL(49) CALL(50)
                CALL(51) CALL(52) CALL(53) CALL(54) CALL(55)
                CALL(56) CALL(57) CALL(58) CALL(59) CALL(60)
                CALL(61) CALL(62) CALL(63) CALL(64) CALL(65)
                CALL(66) CALL(67) CALL(68) CALL(69) CALL(70)
                CALL(71) CALL(72) CALL(73) CALL(74) CALL(75)
                CALL(76) CALL(77) CALL(78) CALL(79) CALL(80)
                CALL(81) CALL(82) CALL(83) CALL(84) CALL(85)
                CALL(86) CALL(87) CALL(88) CALL(89) CALL(90)
                CALL(91) CALL(92) CALL(93) CALL(94) CALL(95)
                CALL(96) CALL(97) CALL(98) CALL(99) CALL(100)
                #undef CALL
            }
        } catch (...) {
            std::cout << "Exception" << i << std::endl;
        }
    }

    return 0;
}
