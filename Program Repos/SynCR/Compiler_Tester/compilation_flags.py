  # Comprehensive list of compiler flags to test (700+ combinations)
maximum_base_flags = {
            # Standard warning flags
            'warnings': [
                '-Wall', '-Wextra', '-pedantic',
                '-Wconversion', '-Wshadow',
                '-Wcast-qual', '-Wwrite-strings',
                '-Wformat=2', '-Wformat-overflow=2',
                '-Wformat-truncation=2', '-Wformat-security',
                '-Wnull-dereference', '-Wstack-protector',
                '-Wtrampolines', '-Wfloat-equal',
                '-Wtraditional-conversion', '-Wdeclaration-after-statement',
                '-Wundef', '-Wuninitialized',
                '-Wstrict-overflow=5', '-Warray-bounds=2',
                '-Wshift-overflow=2', '-Wduplicated-cond',
                '-Wduplicated-branches', '-Wlogical-op',
                '-Wrestrict',
                '-Wdouble-promotion', '-Wimplicit-fallthrough=5',
                # '-Wnull-pointer-subtraction',  -Werror
            ],
            # If warnings needed to be treated as errors add  -Werror
            
            # Optimization flags
            'optimizations': [
                '-O0', '-O1', '-O2', '-O3', '-Os', '-Ofast', '-Og',
                '-fno-strict-aliasing', '-fstrict-aliasing',
                '-fstrict-overflow', '-fno-strict-overflow',
                '-ffast-math', '-fno-fast-math',
                '-funsafe-math-optimizations', '-fno-unsafe-math-optimizations',
                '-ffinite-math-only', '-fno-finite-math-only',
                '-fexcess-precision=fast', '-fexcess-precision=standard',
                '-frounding-math', '-fno-rounding-math',
                '-fsignaling-nans', '-fno-signaling-nans',
                '-fcx-limited-range', '-fno-cx-limited-range',
                '-fipa-pta', '-fno-ipa-pta',
                '-fipa-ra', '-fno-ipa-ra',
                '-fipa-cp', '-fno-ipa-cp',
                '-flto', '-fno-lto',
                '-fwhole-program', '-fno-whole-program',
            ],
            
            # Sanitizers (great for finding bugs)
            'sanitizers': [
                '-fsanitize=address',
                '-fsanitize=undefined',
                '-fsanitize=leak',
                '-fsanitize=thread',
                '-fsanitize=memory',
                '-fsanitize=bool',
                '-fsanitize=bounds',
                '-fsanitize=enum',
                '-fsanitize=float-cast-overflow',
                '-fsanitize=float-divide-by-zero',
                '-fsanitize=nonnull-attribute',
                '-fsanitize=null',
                '-fsanitize=object-size',
                '-fsanitize=return',
                '-fsanitize=returns-nonnull-attribute',
                '-fsanitize=shift',
                '-fsanitize=signed-integer-overflow',
                '-fsanitize=unreachable',
                '-fsanitize=vla-bound',
                '-fsanitize=vptr',
                '-fsanitize=alignment',
            ],
            
            # Language standard versions
            'standards': {
                'c': [
                    '-std=c89', '-std=gnu89',
                    '-std=c99', '-std=gnu99',
                    '-std=c11', '-std=gnu11',
                    '-std=c17', '-std=gnu17',
                    '-std=c2x', '-std=gnu2x',
                ],
                'c++': [
                    '-std=c++98', '-std=gnu++98',
                    '-std=c++11', '-std=gnu++11',
                    '-std=c++14', '-std=gnu++14',
                    '-std=c++17', '-std=gnu++17',
                    '-std=c++20', '-std=gnu++20',
                    '-std=c++23', '-std=gnu++23',
                ]
            },
            
            # Architecture and ABI flags
            'architecture': [
                '-m32', '-m64',
                '-mx32', '-march=native',
                '-mtune=native', '-mavx',
                '-mavx2', '-msse4.2',
                '-mfpmath=sse', '-mfpmath=387',
                '-msoft-float', '-mhard-float',
                '-mabi=sysv', '-mabi=ms',
            ],
            
            # Code generation flags
            'codegen': [
                '-fpic', '-fPIC',
                '-fpie', '-fPIE',
                '-fno-common', '-fcommon',
                '-fshort-wchar', '-fno-short-wchar',
                '-fshort-enums', '-fno-short-enums',
                '-fpack-struct', '-fno-pack-struct',
                '-fleading-underscore', '-fno-leading-underscore',
                '-fmerge-all-constants', '-fno-merge-all-constants',
                '-fstack-check', '-fno-stack-check',
                '-fstack-protector', '-fstack-protector-strong',
                '-fstack-protector-all', '-fno-stack-protector',
                '-fno-omit-frame-pointer', '-fomit-frame-pointer',
                '-fno-asynchronous-unwind-tables', '-fasynchronous-unwind-tables',
                '-fno-exceptions', '-fexceptions',
                '-fno-rtti', '-frtti',
                '-fno-threadsafe-statics', '-fthreadsafe-statics',
            ],
            
            # Debugging flags
            'debug': [
                '-g', '-g0', '-g1', '-g2', '-g3',
                '-ggdb', '-gstabs', '-gstabs+',
                '-gcoff', '-gxcoff', '-gxcoff+',
                '-gdwarf', '-gdwarf-2', '-gdwarf-3', '-gdwarf-4', '-gdwarf-5',
                '-fvar-tracking', '-fvar-tracking-assignments',
                '-fdebug-types-section', '-fno-debug-types-section',
            ],
        }


minimal_base_flags = {
    'warnings': [
        '-Wall',              # Enable most essential warnings
        '-Wextra',            # Add additional useful warnings
        '-Wconversion',       # Catch implicit type conversions
        '-Wshadow'            # Detect variable shadowing
    ],

    'optimizations': [
        '-O0',                # No optimization (baseline)
        '-O2',                # Balanced optimizations
        '-O3',                # Aggressive optimizations
        '-Ofast',             # May break standards, triggers bugs
        '-fno-strict-aliasing',  # Reveal aliasing-related issues
        '-ffast-math',           # Unsafe floating-point optimizations
    ],

    'sanitizers': [
        '-fsanitize=address',     # Memory safety
        '-fsanitize=undefined',   # Detect undefined behavior
        '-fsanitize=leak'         # Memory leak detector
    ],

    'standards': {
        'c': [
            '-std=c99',
            '-std=c11'
        ],
        'c++': [
            '-std=c++11',
            '-std=c++17',
            '-std=c++20'
        ]
    },

    'architecture': [
        '-m64',                # 64-bit architecture
        '-march=native',       # Leverages host-specific features
        '-mavx2'               # Stress vectorized backend
    ],

    'codegen': [
        '-fPIC',                   # Position-independent code
        '-fstack-protector-strong',  # Security against stack overflows
        '-fno-common'             # Enforces strict symbol rules
    ],

    'debug': [
        '-g2',                     # Moderate debug info
        '-gdwarf-4',               # DWARF v4 (widely supported)
        '-fvar-tracking'           # Improves debug clarity
    ]
}
