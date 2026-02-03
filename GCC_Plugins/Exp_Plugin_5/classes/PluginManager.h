#ifndef PLUGIN_MANAGER_H
#define PLUGIN_MANAGER_H

namespace MyGCCPlugin {
    class PluginManager {
    public:
        static void register_plugin(const char* name);
        static void initialize_plugin();
    };
}

#endif // PLUGIN_MANAGER_H
