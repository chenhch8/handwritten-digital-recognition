#include "wraping.h"

int main() {
	Wraping wrap;
	string dirname = "../../img/testData/tmp/";
	wrap.start(dirname + "1.bmp");
	wrap.start(dirname + "2.bmp");
	wrap.start(dirname + "3.bmp");
	wrap.start(dirname + "4.bmp");
	// wrap.start(dirname + "5.bmp");

	return 0;
}

// g++ main.cpp -O2 -L/usr/X11R6/lib -lm -lpthread -lX11
