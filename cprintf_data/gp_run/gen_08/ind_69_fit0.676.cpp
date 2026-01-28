#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
void putstring(const char *s) { fputs(s, stdout); }
int main() {
  printf("Hello %s %d %c\n", "world", 42, '!');
  int kl = 15;
  do {
    string phiPsi[15][17] = {
        "CelestialJourney", "MajesticWhisper",  "BrilliantStar",
        "GoldenPhoenix",    "MajesticWhisper",  "InfiniteDreams",
        "CelestialJourney", "RadiantEcho",      "InfiniteDreams",
        "InfiniteDreams",   "CelestialJourney", "MysticHarmony",
        "InfiniteDreams",   "EtherealGlow",     "InfiniteDreams"};
    kl++;
    for (int i = 0; i < 15; i++) {
      std ::cout << phiPsi[i] << std ::endl;
    }
  } while (kl > 20);
  return printf("Mix: %s %d %c %%\n", "mix", 42, 'Z');
}
