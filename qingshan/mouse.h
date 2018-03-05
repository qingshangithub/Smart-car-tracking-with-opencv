#ifndef MOUSE_H_INCLUDED
#define MOUSE_H_INCLUDED
#include"variable.h"
void onMouse1(int mouseevent, int x, int y, int flags, void* param) {
	if (mouseevent == CV_EVENT_LBUTTONDOWN) {
		if (pointCount[0] < 4) {
			originPoints[pointCount[0]++] = Point2f(x, y);
		}
		else {
			if (pointCount[0] == 4) {
				pointCount[0] = 0;
				originPoints[pointCount[0]++] = Point2f(x, y);
			}
		}
	}
}
#endif