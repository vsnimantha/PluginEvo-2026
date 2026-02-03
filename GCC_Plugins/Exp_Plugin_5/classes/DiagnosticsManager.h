#ifndef DIAGNOSTICS_MANAGER_H
#define DIAGNOSTICS_MANAGER_H

namespace MyGCCPlugin {
    class DiagnosticsManager {
    public:
        static void log_custom_message(const char* message);
    };
}

#endif // DIAGNOSTICS_MANAGER_H
