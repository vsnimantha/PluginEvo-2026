// DFED_Plugin.cpp:127-129  — BUG A: missing return (root cause of segfault)
const char* DFED_PLUGIN::findArgumentValue(const char* key){
	DFED_PLUGIN::findArgumentValue(key, args, argc);   // <-- MISSING 'return' => UB, returns garbage
}

// DFED_Plugin.cpp:139-148 — BUG B: dangling pointer throw (use-after-scope)
const char* DFED_PLUGIN::findArgumentValue(const char* key, const struct plugin_argument *args, int argc) {
	for (int i=0; i< argc; i++){
		if(!strcmp(args[i].key, key)){
			return args[i].value;
		}
	}
	char msg[1024];                                   // local buffer
	snprintf(msg, 1024, "Argument %s not found!...", key, "...");
	throw (const char*) msg;                          // <-- throws pointer to local (dangling)
}

// DFED_Plugin.cpp:167 — CRASH SITE: strlen on undefined f
//   const char* f = findArgumentValue("function");  // f = garbage (Bug A)
//   else if(strlen(f) == 0){                          // strlen(garbage) => SEGFAULT
