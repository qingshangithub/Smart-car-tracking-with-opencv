#ifndef PERSPECTIVE_H_INCLUDED
#define PERSPECTIVE_H_INCLUDED
#include"variable.h"
void Perspective() {
	setMouseCallback("originImage", onMouse1);//��ȡԭͼ���ĸ�����
	Mat warpMatrix = getPerspectiveTransform(originPoints, newPoints);//��ñ任����
	rotated = getStructuringElement(MORPH_RECT, Size(500, 500));
	warpPerspective(frame, rotated, warpMatrix, rotated.size(), INTER_LINEAR, BORDER_CONSTANT);//͸�ӱ任
	namedWindow("perspective");
	imshow("perspective", rotated);
	
}
#endif
