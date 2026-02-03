#include <gcc-plugin.h>
#include <plugin.h>
#include <diagnostic.h>

int plugin_is_GPL_compatible;

// static void detect_global_variable(void *gcc_data, void *user_data) {
//     if (!cfun) { // If outside a function, it’s likely a global variable
//         warning(0, "Global variable detected! Consider using local scope if possible.");
//     }else{
//         warning(1, "Global variable not detected!");
//         if(true){
//             warning(0, "True");
    
//         }
//     }



// }

static void detect_global_variable(void *gcc_data, void *user_data) {
    if (!cfun) { 
        // If outside a function, it's likely a global variable
        warning(0, "Global variable detected! Consider using local scope if possible.");
    } else {
        warning(1, "Global variable not detected");

        // Check if the function is too long (more than 30 lines)
        int num_lines = expand_location(cfun->function_start_locus).line;
        if (num_lines > 30) {
            warning(0, "Function exceeds 30 lines. Consider refactoring");
        }

        // Default condition for demonstration
        if (true) {
            warning(0, "True condition reached.");
        }
    }
}


int plugin_init(struct plugin_name_args *plugin_info, struct plugin_gcc_version *version) {
    register_callback(plugin_info->base_name, PLUGIN_PASS_EXECUTION, detect_global_variable, nullptr);
    return 0;
}




// g++ -shared -fPIC -o my_plugin.so plugin.cpp -I$(gcc -print-file-name=plugin)/include
