#include <gcc-plugin.h>
#include <plugin-version.h>
#include <tree.h>
#include <print-tree.h>

int plugin_is_GPL_compatible;

static void walk_ast(void *gcc_data, void *user_data) {
    tree t = (tree)gcc_data;
    if (TREE_CODE(t) == FUNCTION_DECL) {
        printf("Found function: %s\n", IDENTIFIER_POINTER(DECL_NAME(t)));
    }
}

int plugin_init(struct plugin_name_args *plugin_info,
                struct plugin_gcc_version *version) {
    register_callback(plugin_info->base_name,
                     PLUGIN_PRE_GENERICIZE,
                     walk_ast,
                     NULL);
    return 0;
}

// g++ -shared -fPIC -o my_plugin.so plugin.cpp my_passes.cpp -I$(gcc -print-file-name=plugin)/include

