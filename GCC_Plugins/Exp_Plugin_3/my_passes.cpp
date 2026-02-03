#include "my_passes.h"

void FunctionPass::execute() {
    std::cout << "FunctionPass: Processing function!" << std::endl;
}

void VariablePass::execute() {
    std::cout << "VariablePass: Processing variable!" << std::endl;
}
