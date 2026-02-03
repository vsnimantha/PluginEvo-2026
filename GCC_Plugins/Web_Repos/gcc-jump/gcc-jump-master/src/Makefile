INSTALLDIR ?= /home/chenkan/work/gcc-local
PLUGINDIR = $(shell $echo g++ -print-file-name=plugin)

all:
	g++-10 plugin.cpp gcj.cpp -I/usr/lib/gcc/x86_64-linux-gnu/14/plugin/include -fPIC -g -shared -o gcj.so -Wall
	g++-10 main.cpp gcj.cpp elf.cpp -g -o gcj -Wall
	#g++ elf.cpp -DTEST -g -o test -Wall
