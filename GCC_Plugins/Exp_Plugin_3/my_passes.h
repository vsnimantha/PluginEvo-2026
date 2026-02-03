#ifndef MY_PASSES_H
#define MY_PASSES_H

#include <iostream>

class CustomPass {
public:
    virtual void execute() = 0; // Pure virtual function
    virtual ~CustomPass() {}
};

class FunctionPass : public CustomPass {
public:
    void execute() override;
};

class VariablePass : public CustomPass {
public:
    void execute() override;
};

#endif // MY_PASSES_H
