// #include "logger.h"
// #include <fstream>
// #include <iostream>
// #include <sstream>
// #include <ctime>
// #include <cxxabi.h>
// #include <execinfo.h>
// #include <sys/stat.h>
// #include <sys/types.h>

// // // Example definition of plugin_gcc_version
// // struct plugin_gcc_version {
// //     int major;
// //     int minor;
// //     std::string patchlevel;
// // };

// // // Overloading operator<< for plugin_gcc_version
// // std::ostream& operator<<(std::ostream& os, const plugin_gcc_version& version) {
// //     os << version.major << "." << version.minor << "." << version.patchlevel;
// //     return os;
// // }

// // // Example definition of plugin_name_args
// // struct plugin_name_args {
// //     std::string name;
// //     std::string args;
// // };

// // // Overloading operator<< for plugin_name_args
// // std::ostream& operator<<(std::ostream& os, const plugin_name_args& pna) {
// //     os << "Name: " << pna.name << ", Args: " << pna.args;
// //     return os;
// // }

// std::string demangle(const char* name) {
//     int status = -1;
//     char* demangled = abi::__cxa_demangle(name, NULL, NULL, &status);
//     std::string result((status == 0) ? demangled : name);
//     free(demangled);
//     return result;
// }

// std::string get_current_timestamp() {
//     time_t currentTime = time(nullptr);
//     char timeString[100];
//     strftime(timeString, sizeof(timeString), "%Y-%m-%d_%H-%M-%S", localtime(&currentTime));
//     return std::string(timeString);
// }

// std::string get_backtrace_filename(const std::string& log_filename) {
//     return log_filename + "_backtrace.log";
// }

// void universal_log(int log_type, const char* file_name, const char* function_name, int log_line, const std::string& message, const std::string& args_str, const std::string& corresponding_code, int corresponding_line) {
//     struct stat info;
//     if (stat("Logs", &info) != 0) {
//         if (mkdir("Logs", 0777) != 0) {
//             std::cerr << "Failed to create Logs directory" << std::endl;
//             return;
//         }
//     }
//     std::string log_filename = "Logs/" + std::string(file_name) + "_" + get_current_timestamp() + ".log";
//     std::ofstream log_file(log_filename, std::ios_base::app);
//     if (!log_file.is_open()) {
//         std::cerr << "Failed to open log file: " << log_filename << std::endl;
//         return;
//     }
//     switch (log_type) {
//         case 0: // ENTRY
//             log_file << "----------------------------------------" << "\n";
//             log_time(log_file);
//             log_file << "Entering function\n";
//             break;
//         case 1: // EXIT
//             log_file << "Exiting function\n";
//             log_file << "----------------------------------------" << "\n";
//             break;
//         case 2: // INTERMEDIATE
//             log_file << "----------------------------------------" << "\n";
//             log_time(log_file);
//             break;
//     }
//     log_function_data(log_file, file_name, function_name, log_line, message, args_str, corresponding_code, corresponding_line);
//     log_file.close();
//     std::cerr << "Log entry written successfully: " << log_filename << std::endl;  // Debug print to confirm writing
//     if (log_type == 1) {
//         std::string backtrace_filename = get_backtrace_filename(log_filename);
//         log_backtrace(backtrace_filename);
//     }
// }

// void log_time(std::ofstream& log_file) {
//     time_t currentTime = time(nullptr);
//     char timeString[100];
//     strftime(timeString, sizeof(timeString), "%Y-%m-%d %H:%M:%S", localtime(&currentTime));
//     log_file << "[" << timeString << "]\n";
// }

// void log_function_data(std::ofstream& log_file, const char* file_name, const char* function_name, int log_line, const std::string& message, const std::string& args_str, const std::string& corresponding_code, int corresponding_line) {
//     log_file << "File Name: " << file_name << "\n";
//     log_file << "Function: " << function_name << " (log line: " << log_line << ")\n";
//     log_file << "Message: " << message << "\n";
//     log_file << "Arguments: " << args_str << "\n";
//     log_file << "Corresponding Code: " << corresponding_code << "\n";
//     log_file << "Corresponding Line: " << (corresponding_line-1) << "\n";
// }

// void log_backtrace(const std::string& filename) {
//     std::ofstream log_file(filename, std::ios_base::app);
//     if (!log_file.is_open()) {
//         std::cerr << "Failed to open backtrace log file: " << filename << std::endl;
//         return;
//     }
//     void* array[10];
//     size_t size = backtrace(array, 10);
//     char** symbols = backtrace_symbols(array, size);
//     if (symbols) {
//         for (size_t i = 0; i < size; ++i) {
//             log_file << demangle(symbols[i]) << "\n";
//         }
//         free(symbols);
//     }
//     log_file.close();
//     std::cerr << "Backtrace written successfully: " << filename << std::endl; // Debug print to confirm writing
// }


#include "logger.h"
#include <fstream>
#include <iostream>
#include <sstream>
#include <ctime>
#include <cxxabi.h>
#include <execinfo.h>
#include <sys/stat.h>
#include <sys/types.h>

// Example definition of plugin_gcc_version
struct plugin_gcc_version {
    int major;
    int minor;
    std::string patchlevel;
};

// Overloading operator<< for plugin_gcc_version
std::ostream& operator<<(std::ostream& os, const plugin_gcc_version& version) {
    os << version.major << "." << version.minor << "." << version.patchlevel;
    return os;
}

// Example definition of plugin_name_args
struct plugin_name_args {
    std::string name;
    std::string args;
};

// Overloading operator<< for plugin_name_args
std::ostream& operator<<(std::ostream& os, const plugin_name_args& pna) {
    os << "Name: " << pna.name << ", Args: " << pna.args;
    return os;
}

std::string demangle(const char* name) {
    int status = -1;
    char* demangled = abi::__cxa_demangle(name, NULL, NULL, &status);
    std::string result((status == 0) ? demangled : name);
    free(demangled);
    return result;
}

std::string get_current_timestamp() {
    time_t currentTime = time(nullptr);
    char timeString[100];
    strftime(timeString, sizeof(timeString), "%Y-%m-%d_%H-%M-%S", localtime(&currentTime));
    return std::string(timeString);
}

std::string get_backtrace_filename(const std::string& log_filename) {
    return log_filename + "_backtrace.log";
}

void universal_log(int log_type, const char* file_name, const char* function_name, int log_line, const std::string& message, const std::string& args_str, const std::string& corresponding_code, int corresponding_line) {
    struct stat info;
    if (stat("Logs", &info) != 0) {
        if (mkdir("Logs", 0777) != 0) {
            std::cerr << "Failed to create Logs directory" << std::endl;
            return;
        }
    }
    std::string log_filename = "Logs/" + std::string(file_name) + "_" + get_current_timestamp() + ".log";
    std::ofstream log_file(log_filename, std::ios_base::app);
    if (!log_file.is_open()) {
        std::cerr << "Failed to open log file: " << log_filename << std::endl;
        return;
    }
    switch (log_type) {
        case 0: // ENTRY
            log_file << "----------------------------------------" << "\n";
            log_time(log_file);
            log_file << "Entering function\n";
            break;
        case 1: // EXIT
            log_file << "Exiting function\n";
            log_file << "----------------------------------------" << "\n";
            break;
        case 2: // INTERMEDIATE
            log_file << "----------------------------------------" << "\n";
            log_time(log_file);
            break;
    }
    log_function_data(log_file, file_name, function_name, log_line, message, args_str, corresponding_code, corresponding_line);
    log_file.close();
    std::cerr << "Log entry written successfully: " << log_filename << std::endl;  // Debug print to confirm writing
    if (log_type == 1) {
        std::string backtrace_filename = get_backtrace_filename(log_filename);
        log_backtrace(backtrace_filename);
    }
}

void log_time(std::ofstream& log_file) {
    time_t currentTime = time(nullptr);
    char timeString[100];
    strftime(timeString, sizeof(timeString), "%Y-%m-%d %H:%M:%S", localtime(&currentTime));
    log_file << "[" << timeString << "]\n";
}

void log_function_data(std::ofstream& log_file, const char* file_name, const char* function_name, int log_line, const std::string& message, const std::string& args_str, const std::string& corresponding_code, int corresponding_line) {
    log_file << "File Name: " << file_name << "\n";
    log_file << "Function: " << function_name << " (log line: " << log_line << ")\n";
    log_file << "Message: " << message << "\n";
    log_file << "Arguments: " << args_str << "\n";
    log_file << "Corresponding Code: " << corresponding_code << "\n";
    log_file << "Corresponding Line: " << corresponding_line << "\n";
}

void log_backtrace(const std::string& filename) {
    std::ofstream log_file(filename, std::ios_base::app);
    if (!log_file.is_open()) {
        std::cerr << "Failed to open backtrace log file: " << filename << std::endl;
        return;
    }
    void* array[10];
    size_t size = backtrace(array, 10);
    char** symbols = backtrace_symbols(array, size);
    if (symbols) {
        for (size_t i = 0; i < size; ++i) {
            log_file << demangle(symbols[i]) << "\n";
        }
        free(symbols);
    }
    log_file.close();
    std::cerr << "Backtrace written successfully: " << filename << std::endl; // Debug print to confirm writing
}