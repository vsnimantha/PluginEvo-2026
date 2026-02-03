#include "DiagnosticsManager.h"
#include <cstdio>

namespace MyGCCPlugin {
    void DiagnosticsManager::log_custom_message(const char* message) {
        printf("Diagnostics: %s\n", message);
    }
}
