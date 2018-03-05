#pragma once

#include <Python.h>
#include <string>
#include <sstream>
#include "car.h"

using std::stringstream;
using std::string;

void initializePython()
{
	Py_Initialize();
	PyRun_SimpleString("from car import Car");
	PyRun_SimpleString("car = Car('192.168.137.94', 5555, 0.5, 0.25)");
	PyRun_SimpleString("print(car)");
}

void setStraightSpeed(double speed)
{
	stringstream cmd;
	string a = "car.set_straight_speed(", b = ")";
	cmd << a << speed << b;
	PyRun_SimpleString(cmd.str().c_str());
}

void setTurnBias(double bias)
{
	stringstream cmd;
	string a = "car.set_turn_bias(", b = ")";
	cmd << a << bias << b;
	PyRun_SimpleString(cmd.str().c_str());
}

void stop()
{
	PyRun_SimpleString("car.stop()");
}
