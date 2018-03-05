#ifndef PERSPECTIVE_H_INCLUDED
#define PERSPECTIVE_H_INCLUDED
#include"variable.h"
void Perspective() {
	setMouseCallback("originImage", onMouse1);//读取原图的四个顶点
	Mat warpMatrix = getPerspectiveTransform(originPoints, newPoints);//获得变换矩阵
	rotated = getStructuringElement(MORPH_RECT, Size(500, 500));
	warpPerspective(frame, rotated, warpMatrix, rotated.size(), INTER_LINEAR, BORDER_CONSTANT);//透视变换
	namedWindow("perspective");
	imshow("perspective", rotated);
	
}
#endif
