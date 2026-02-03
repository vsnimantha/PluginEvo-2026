#include "PluginManager.h"
#include <cstdio>

namespace MyGCCPlugin {
    void PluginManager::register_plugin(const char* name) {
        printf("Plugin registered: %s\n", name);
    }

    void PluginManager::initialize_plugin() {
        printf("Plugin initialized.\n");
        // Additional initialization logic can be added here.
    }
}
