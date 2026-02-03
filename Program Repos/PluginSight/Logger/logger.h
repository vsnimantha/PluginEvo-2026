// #ifndef LOGGER_H
// #define LOGGER_H

// #include <string>
// #include <fstream>
// #include <execinfo.h>
// #include <cxxabi.h>
// #include <sstream>
// #include <iostream>
// #include <vector>
// #include <typeinfo>

// std::string demangle(const char* name);
// void universal_log(int log_type, const char* file_name, const char* function_name, int log_line, const std::string& message, const std::string& args_str, const std::string& corresponding_code, int corresponding_line);

// #define LOG_FUNCTION_START(corresponding_code, corresponding_line, ...) \
//     universal_log(0, __FILE__, __func__, __LINE__, "Entering function", args_to_string(__VA_ARGS__), corresponding_code, corresponding_line)
// #define LOG_FUNCTION_END(corresponding_code, corresponding_line, ...) \
//     universal_log(1, __FILE__, __func__, __LINE__, "Exiting function", args_to_string(__VA_ARGS__), corresponding_code, corresponding_line)
// #define LOG_INTERMEDIATE(log_line, message, corresponding_code, corresponding_line, ...) \
//     universal_log(2, __FILE__, __func__, log_line, message, args_to_string(__VA_ARGS__), corresponding_code, corresponding_line)

// template<typename T>
// std::string get_type_name() { return typeid(T).name(); }

// template<typename T>
// std::string arg_info(const std::string& var_name, const T& var) {
//     std::ostringstream oss;
//     oss << var_name << " (" << get_type_name<T>() << ") = " << var;
//     return oss.str();
// }

// template<typename T>
// std::string make_arg_pair(const char* name, const T& value) {
//     std::ostringstream oss;
//     oss << name << " (" << get_type_name<T>() << ") = " << value;
//     return oss.str();
// }

// template <typename... Args>
// std::string args_to_string(const Args&... args) {
//     std::ostringstream stream;
//     ((stream << args << ", "), ...);
//     std::string result = stream.str();
//     if (!result.empty()) {
//         result.pop_back();
//         result.pop_back(); // Remove trailing comma and space
//     }
//     return result;
// }

// void log_time(std::ofstream& log_file);
// void log_function_data(std::ofstream& log_file, const char* file_name, const char* function_name, int log_line, const std::string& message, const std::string& args_str, const std::string& corresponding_code, int corresponding_line);
// void log_backtrace(const std::string& filename);

// #endif // LOGGER_H


#ifndef LOGGER_H
#define LOGGER_H

#include <string>
#include <fstream>
#include <execinfo.h>
#include <cxxabi.h>
#include <sstream>
#include <iostream>
#include <vector>
#include <typeinfo>

std::string demangle(const char* name);
void universal_log(int log_type, const char* file_name, const char* function_name, int log_line, const std::string& message, const std::string& args_str, const std::string& corresponding_code, int corresponding_line);

#define LOG_FUNCTION_START(corresponding_code, corresponding_line, ...) \
    universal_log(0, __FILE__, __func__, __LINE__, "Entering function", args_to_string(__VA_ARGS__), corresponding_code, corresponding_line)
#define LOG_FUNCTION_END(corresponding_code, corresponding_line, ...) \
    universal_log(1, __FILE__, __func__, __LINE__, "Exiting function", args_to_string(__VA_ARGS__), corresponding_code, corresponding_line)
#define LOG_INTERMEDIATE(log_line, message, corresponding_code, corresponding_line, ...) \
    universal_log(2, __FILE__, __func__, log_line, message, args_to_string(__VA_ARGS__), corresponding_code, corresponding_line)

template<typename T>
std::string get_type_name() { return typeid(T).name(); }

template<typename T>
std::string arg_info(const std::string& var_name, const T& var) {
    std::ostringstream oss;
    oss << var_name << " (" << get_type_name<T>() << ") = " << var;
    return oss.str();
}

template<typename T>
std::string make_arg_pair(const char* name, const T& value) {
    std::ostringstream oss;
    oss << name << " (" << get_type_name<T>() << ") = " << value;
    return oss.str();
}

template <typename... Args>
std::string args_to_string(const Args&... args) {
    std::ostringstream stream;
    ((stream << args << ", "), ...);
    std::string result = stream.str();
    if (!result.empty()) {
        result.pop_back();
        result.pop_back(); // Remove trailing comma and space
    }
    return result;
}

void log_time(std::ofstream& log_file);
void log_function_data(std::ofstream& log_file, const char* file_name, const char* function_name, int log_line, const std::string& message, const std::string& args_str, const std::string& corresponding_code, int corresponding_line);
void log_backtrace(const std::string& filename);

#endif // LOGGER_H
