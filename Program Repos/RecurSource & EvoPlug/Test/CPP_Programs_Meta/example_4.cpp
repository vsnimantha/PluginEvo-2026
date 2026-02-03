#include <iostream>
#include <vector>
#include <thread>
#include <mutex>

std::mutex mtx;
std::vector<int> primes;

bool isPrime(int n) {
    if (n < 2) return false;
    for (int i = 2; i*i <= n; ++i)
        if (n % i == 0) return false;
    return true;
}

void findPrimes(int start, int end) {
    for (int i = start; i <= end; ++i) {
        if (isPrime(i)) {
            std::lock_guard<std::mutex> lock(mtx);
            primes.push_back(i);
        }
    }
}

int main() {
    int range = 1000;
    std::thread t1(findPrimes, 1, range / 2);
    std::thread t2(findPrimes, range / 2 + 1, range);

    t1.join();
    t2.join();

    std::cout << "Primes found: " << primes.size() << "\n";
    return 0;
}
