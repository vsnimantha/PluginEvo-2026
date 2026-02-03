#include "gcc-plugin.h"
#include "plugin-version.h"
#include "classes/PluginManager.h"
#include "classes/DiagnosticsManager.h"
#include "classes/VariableTracker.h"

using namespace MyGCCPlugin;

int plugin_is_GPL_compatible;

int plugin_init(struct plugin_name_args* plugin_info,
                struct plugin_gcc_version* version) {
    // Using namespace explicitly for PluginManager functions
    PluginManager::register_plugin(plugin_info->base_name);
    PluginManager::initialize_plugin();

     // Example of using DiagnosticsManager
    DiagnosticsManager::log_custom_message("Compilation started successfully!");
    VariableTracker::track_variable_decls();
    return 0;
}

// g++ -shared -fPIC -o my_plugin.so plugin.cpp classes/PluginManager.cpp -I/usr/lib/gcc/x86_64-linux-gnu/14/plugin/include -I./classes

// g++ -shared -fPIC -o my_plugin.so plugin.cpp classes/VariableTracker.cpp classes/DiagnosticsManager.cpp classes/PluginManager.cpp -I/usr/lib/gcc/x86_64-linux-gnu/14/plugin/include -I./classes
