// test_plugin_coverage.cpp
// This file is designed to maximize coverage of your GCC plugin
// Template_8
#include <cstdio>
#include <iostream>
#include <string>
#include <vector>

using namespace std;

// Test cases for different log levels
void test_log_levels() {
  printf("Testing log levels\n");
  // These should be controlled by plugin parameters
}

// Test cases for printf functionality
void test_printf_functions() {
  // Basic printf
  printf("Standard printf: %d %f %s\n", 42, 3.14, "test");

  // Different format specifiers
  printf("Char: %c\n", 'A');
  printf("String: %s\n", "hello");
  printf("Integer: %d\n", -123);
  printf("Unsigned: %u\n", 456);
  printf("Hex: %x\n", 0xABC);
  printf("Float: %f\n", 3.14159);
  printf("Scientific: %e\n", 123.456);
  printf("Pointer: %p\n", (void *)0x12345678);

  // Width and precision
  printf("Width: %10d\n", 42);
  printf("Precision: %.2f\n", 3.14159);
  printf("Combined: %10.2f\n", 3.14159);

  // Multiple args
  printf("Multiple: %d %f %s\n", 1, 2.3, "four");
}

// Edge cases
void test_edge_cases() {
  // Empty string
  printf("");

  // Missing arguments (should trigger warnings)
  printf("%d");
  printf("%d %d", 1);

  // Extra arguments
  printf("%d", 1, 2, 3);

  // Invalid format specifiers
  printf("%z\n");
  printf("%q\n");
}

// Different scopes
namespace test {
void nested_printf() { printf("Nested namespace printf\n"); }
} // namespace test

class TestClass {
public:
  void member_printf() { printf("Member function printf\n"); }

  static void static_printf() { printf("Static member printf\n"); }
};

// Template functions
template <typename T> void template_printf(T value) {
  printf("Template value: %d\n", static_cast<int>(value));
}
int psiFunc(int num, int index) {
  double rho = 67.15980980807869;
  if (index >= 5) {
    return num;
  }
  return psiFunc(num, index - 1);
}
double nuFunc() {
  std::cout << "Default output text" << std::endl;
  return 59.444469477086926;
}
double gammaFunc(int muLambdaParam, float psiParam, string lambdaBetaParam) {
  bool gammaTheta = false;
  return 70.98096960190064;
}
// Main function with various test cases
int main() {
  // Basic tests
  test_log_levels();
  test_printf_functions();
  test_edge_cases();

  // Different contexts
  test::nested_printf();

  TestClass obj;
  obj.member_printf();
  TestClass::static_printf();

  // Template instantiation
  template_printf(42);
  template_printf(3.14);

  // Multiple calls
  for (int i = 0; i < 5; i++) {
    printf("Loop iteration: %d\n", i);
  }

  // Conditional printf
  if (printf("Conditional printf\n")) {
    printf("Inside if\n");
  }

  bool tauPi[11] = {true,  true,  true,  false, true, true,
                    false, false, false, true,  true};
  for (int i = 0; i < 11; i++) {
    std::cout << tauPi[i] << std::endl;
  }

  psiFunc(10, 20);
  int kl = 10;
  do {
    printf("Connection lost");
    kl++;
  } while (kl <= 5);
  for (int i = 5; i < 10; i++) {
    printf("VXCZBEBA3NYZ8254HNYI");
  }

  nuFunc();
  int muLambdaParam = 39;
  float psiParam = 2.1540804993549267f;
  string lambdaBetaParam = "S5LF96MPRU";

  gammaFunc(muLambdaParam, psiParam, lambdaBetaParam);
  int etaIota = 92;
  if (false) {
    for (int i = 10; i < 15; i++) {
      int zeta[14] = {11, 55, 12, 15, 3, 20, 16, 16, 20, 10, 1, 20, 4, 3};
      for (int i = 0; i < 14; i++) {
        std::cout << zeta[i] << std::endl;
      }
    }
  } else {
    int kl = 20;
    do {
      float alpha[3] = {6.0f, 20.0f, 9.54275789645621f};
      kl++;
      for (int i = 0; i < 3; i++) {
        std::cout << alpha[i] << std::endl;
      }
    } while (kl <= 20);
  }
  double rhoPsi = 9 - 14;
  int ij = 20;
  while (ij < 15) {
    double omegaSigma = 17 / 11;
    ij++;
  }
  std::cout << "Test message 1234" << std::endl;
  std::cout << "EJCNPA5VQV5K9H41GW7B" << std::endl;
  std::cout << "Default output text" << std::endl;
  std::cout << "2K7CBQ0EDC3BE93VCJND" << std::endl;
  bool upsilon = false;

  // Return different values
  return printf("Final message\n") > 0 ? 0 : 1;
}