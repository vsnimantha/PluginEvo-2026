
#include "ExternalClass.h"
#include <iostream>


void ExternalClass::displayMessage(const std::string& message) {

    // Decision 1: Check if the message is empty
    if (message.empty()) {
        std::cerr << "No message to display" << std::endl;
    } else {
        std::cout << message << std::endl;
    }

    // Decision 2: Loop through characters in the message
    for (size_t i = 0; i < message.length(); ++i) {
        char ch = message[i];
        // Decision 3: Check if the character is a vowel
        if (ch == 'a' || ch == 'e' || ch == 'i' || ch == 'o' || ch == 'u' ||
            ch == 'A' || ch == 'E' || ch == 'I' || ch == 'O' || ch == 'U') {
            std::cout << ch << " is a vowel" << std::endl;
        } else {
            std::cout << ch << " is not a vowel" << std::endl;
        }
    }
}
