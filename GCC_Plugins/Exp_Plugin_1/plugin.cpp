#include <gcc-plugin.h>
#include <tree.h>
#include <iostream>

int plugin_is_GPL_compatible;

// Base class for custom GCC passes
class CustomPass {
public:
    virtual void execute() = 0; // Pure virtual function
    virtual ~CustomPass() {}
};

// First pass: Prints a message when processing a function
class FunctionPass : public CustomPass {
public:
    void execute() override {
        std::cout << "FunctionPass: Processing function!" << std::endl;
    }
};

// Second pass: Prints a message when processing a variable
class VariablePass : public CustomPass {
public:
    void execute() override {
        std::cout << "VariablePass: Processing variable!" << std::endl;
    }
};

// Callback function for GCC events
static void my_pass_callback(void *gcc_data, void *) {
    FunctionPass fPass;
    VariablePass vPass;

    fPass.execute();
    vPass.execute();
}

// Plugin Entry Point
int plugin_init(struct plugin_name_args *plugin_info, struct plugin_gcc_version *version) {
    std::cout << "GCC Plugin with Multiple Classes Initialized!" << std::endl;
    register_callback(plugin_info->base_name, PLUGIN_FINISH_DECL, my_pass_callback, nullptr);
    return 0;
}
