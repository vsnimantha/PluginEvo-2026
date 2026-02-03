#include <gcc-plugin.h>
#include "my_passes.h"

int plugin_is_GPL_compatible;

// Callback function for GCC events
static void my_pass_callback(void *gcc_data, void *) {
    FunctionPass fPass;
    VariablePass vPass;

    fPass.execute();
    vPass.execute();
}

// Plugin Entry Point
int plugin_init(struct plugin_name_args *plugin_info, struct plugin_gcc_version *version) {
    std::cout << "GCC Plugin with Separate Files Initialized!" << std::endl;
    register_callback(plugin_info->base_name, PLUGIN_FINISH_DECL, my_pass_callback, nullptr);
    return 0;
}

// g++ -shared -fPIC -o my_plugin.so plugin.cpp my_passes.cpp -I$(gcc -print-file-name=plugin)/include

