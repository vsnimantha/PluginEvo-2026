# Confirmed Bug Record: DFED #1

## Phase 1 — ICE Confirmation
| Field | Value |
|---|---|
| Plugin | DFED (myDFEDPlugin), arm-none-eabi-g++ (GCC 7, cortex-m3) |
| Root-cause function | findArgumentValue, DFED_Plugin.cpp:127 (missing return) |
| Crash site | DFED_Plugin.cpp:167 (strlen on garbage), via gate :58 |
| Class | LOGIC DEFECT — crashes when used correctly |
| Origin | **PLUGIN — CONFIRMED BY TRACE** |
| Static-detectable | YES (-Wreturn-type in -Wall; cppcheck for the dangling throw) |
| Developer-confirmed | YES |

## Console trace
```
test.cpp: In function 'void alpha()':
test.cpp:5:1: internal compiler error: Segmentation fault
0x...  DFED_PLUGIN::isAllowedToRun(char const*)   DFED_Plugin.cpp:167
0x...  DFED_PLUGIN::gate(function*)               DFED_Plugin.cpp:58
```
Command: arm-none-eabi-g++ -mthumb -mcpu=cortex-m3 -march=armv7-m
  -specs=nosys.specs -fplugin=compiled_plugin.so
  -fplugin-arg-compiled_plugin-function=main
  -fplugin-arg-compiled_plugin-techniqueSpecific=FDFC -g test.cpp -o test.o

## Root cause in source
### Bug A (segfault cause) — DFED_Plugin.cpp:127-129
```cpp
const char* DFED_PLUGIN::findArgumentValue(const char* key){
	DFED_PLUGIN::findArgumentValue(key, args, argc);   // <-- MISSING 'return'
}                                                       //     falls off end -> returns garbage
```
Caller (isAllowedToRun): `const char* f = findArgumentValue("function");`
then `strlen(f)` at :167 -> dereferences garbage pointer -> SEGFAULT.

### Bug B (latent) — DFED_Plugin.cpp:139-148
```cpp
const char* DFED_PLUGIN::findArgumentValue(const char* key,
        const struct plugin_argument *args, int argc) {
	for (int i=0; i< argc; i++){
		if(!strcmp(args[i].key, key)){ return args[i].value; }
	}
	char msg[1024];                                     // local buffer
	snprintf(msg, 1024, "Argument %s not found!...", key, "...");
	throw (const char*) msg;                            // <-- dangling: throws ptr to local
}
```

## Phase 2 — Static Backtrack
| Bug | Tool | Result |
|---|---|---|
| A (missing return) | g++ -Wreturn-type (in -Wall) | FLAGGED: "no return statement in function returning non-void" |
| B (dangling throw) | cppcheck | FLAGGED: "Returning pointer to local variable 'msg' [returnDanglingLifetime]" |
BOTH statically detectable. The segfault-causing bug is caught by a DEFAULT
-Wall warning. 2x2 cell: CONFIRMED + STATICALLY-FLAGGED.
