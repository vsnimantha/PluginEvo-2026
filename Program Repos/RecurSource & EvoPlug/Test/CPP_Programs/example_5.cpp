#include <iostream>
#include <memory>

class Resource {
public:
    Resource() { std::cout << "Resource acquired\n"; }
    ~Resource() { std::cout << "Resource released\n"; }
    void use() { std::cout << "Using resource\n"; }

private:
    Resource(const Resource&) = delete; // Disable copy constructor
    Resource& operator=(const Resource&) = delete; // Disable assignment operator
    Resource(Resource&&) = delete;    
};

void process() {
    std::unique_ptr<Resource> res = std::make_unique<Resource>();
    res->use();
}

int main() {
    process();
    std::cout << "Back in main\n";
    return 0;
}
