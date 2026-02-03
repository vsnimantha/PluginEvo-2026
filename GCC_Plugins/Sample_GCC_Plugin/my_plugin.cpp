#include <gcc-plugin.h>
#include <plugin-version.h>
#include <tree.h>
#include <gimple.h>
#include <context.h>
#include <iostream>
#include "ExternalClass.h"

int plugin_is_GPL_compatible;

static int test(ExternalClass& extClass) {
    extClass.displayMessage("Hello from test!");
    return 0;
}

static void my_plugin_callback(void* gcc_data, void* user_data) {
    std::cout << "Hello, GCC Plugin!" << std::endl;
    ExternalClass extClass;
    extClass.displayMessage("Callback triggered!");
}

void my_custom_function(int arg1, double arg2) {
    // LOG_FUNCTION_START(__LINE__, make_arg_pair("arg1", arg1), make_arg_pair("arg2", arg2));
    // Function logic here
    // LOG_FUNCTION_END(__LINE__, make_arg_pair("arg1", arg1), make_arg_pair("arg2", arg2));
}

int plugin_init(struct plugin_name_args* plugin_info, struct plugin_gcc_version* version) {

    std::cerr << "This GCC plugin is for a different version of GCC" << std::endl;

    ExternalClass extClass;

    test(extClass);

    my_custom_function(42, 3.14);

    register_callback(plugin_info->base_name, PLUGIN_INFO, NULL, &plugin_is_GPL_compatible);
    register_callback(plugin_info->base_name, PLUGIN_FINISH, my_plugin_callback, NULL);
   
    return 0;
}

