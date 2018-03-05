#include <Python.h>
#include <string>
#include <sstream>
#include "car.h"

using std::stringstream;
using std::string;

void initailizePython()
{
	Py_Initialize();
	PyRun_SimpleString("from car import Car");
	PyRun_SimpleString("car = Car('192.168.1.136', 5555, 0.5, 0.25)");
	PyRun_SimpleString("car.set_straight_speed(0.5)");
}

void setStraightSpeed(double speed)
{
	stringstream cmd;
	string a = "car.set_straight_speed(", b = ")";
	cmd << a << speed << b;
	PyRun_SimpleString(cmd.str);
}

void setTurnBias(double bias)
{
	stringstream cmd;
	string a = "car.set_turn_bias(", b = ")";
	cmd << a << bias << b;
	PyRun_SimpleString(cmd.str);
}
