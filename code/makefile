all: gibbs_iteration_c.so

gibbs_iteration_c.so: gibbs_iteration_c.pyx
	cython gibbs_iteration_c.pyx
	gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing  -I/usr/include/python2.7 -o gibbs_iteration_c.so gibbs_iteration_c.c
