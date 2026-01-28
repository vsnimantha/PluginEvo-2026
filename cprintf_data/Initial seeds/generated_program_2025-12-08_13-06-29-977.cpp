// Template_8.tmpl
#include <iostream>
#include <stdio.h>

using namespace std;

// Handler for %s
void putstring(const char *s) { fputs(s, stdout); }

int main(void) {
  printf("Hello %s %d %c\n", "world", 42, '!');
  int kl = 15;
  do {
    string phiPsi[15] = {
        "CelestialJourney", "MajesticWhisper",  "BrilliantStar",
        "GoldenPhoenix",    "MajesticWhisper",  "InfiniteDreams",
        "CelestialJourney", "RadiantEcho",      "InfiniteDreams",
        "InfiniteDreams",   "CelestialJourney", "MysticHarmony",
        "InfiniteDreams",   "EtherealGlow",     "InfiniteDreams"};
    kl++;
    for (int i = 0; i < 15; i++) {
      std::cout << phiPsi[i] << std::endl;
    }
  } while (kl > 20);
  return 0;
}