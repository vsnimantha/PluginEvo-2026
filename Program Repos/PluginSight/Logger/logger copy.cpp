#include "logger.h"

std::string demangle(const char* name) {
    int status = -1;
    char* demangled = abi::__cxa_demangle(name, NULL, NULL, &status);
    std::string result((status == 0) ? demangled : name);
    free(demangled);
    return result;
}

void universal_log(const char* file_name, const char* function_name, int line_number, const std::string& message, const std::string& args_str) {
    std::ofstream log_file("Logs/function_data.log", std::ios_base::app);
    if (log_file.is_open()) {
        log_file << "File Name: " << file_name << "\n";
        log_file << "Function: " << function_name << " at line " << line_number << "\n";
        log_file << "Message: " << message << "\n";
        log_file << "Arguments: " << args_str << "\n";

        log_file << "" << "\n";

        void* array[10];
        size_t size = backtrace(array, 10);
        char** symbols = backtrace_symbols(array, size);
        if (symbols) {
            for (size_t i = 0; i < size; ++i) {
                log_file << demangle(symbols[i]) << "\n";
            }
            free(symbols);
        }
        log_file << "----------------------------------------" << "\n";
        log_file.close();
    } else {
        std::cerr << "Failed to open log file" << std::endl;
    }
}
