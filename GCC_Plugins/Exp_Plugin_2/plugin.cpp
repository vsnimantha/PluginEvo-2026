// Magic Number Detector
#include <gcc-plugin.h>
#include <plugin-version.h>
#include <tree.h>
#include <diagnostic.h>

int plugin_is_GPL_compatible;

static void check_magic_nums(void *gcc_data, void *user_data) {
    tree t = (tree)gcc_data;
    if (TREE_CODE(t) == INTEGER_CST && tree_fits_uhwi_p(t)) {
        unsigned val = tree_to_uhwi(t);
        if (val > 10 && val != 16 && val != 32 && val != 64 && val != 128) {
            warning_at(DECL_SOURCE_LOCATION(current_function_decl),
                      0, "Magic number detected: %u", val);
        }
    }
}

int plugin_init(struct plugin_name_args *plugin_info,
                struct plugin_gcc_version *version) {
    register_callback(plugin_info->base_name,
                     PLUGIN_PRE_GENERICIZE,
                     check_magic_nums,
                     NULL);
    return 0;
}