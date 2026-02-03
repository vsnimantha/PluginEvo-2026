#ifndef VARIABLE_TRACKER_H
#define VARIABLE_TRACKER_H

// #include "tree.h"

namespace MyGCCPlugin {
    class VariableTracker {
    public:
        static void track_variable_decls();
    };
}

#endif // VARIABLE_TRACKER_H
