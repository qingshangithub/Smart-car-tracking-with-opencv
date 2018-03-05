#include<iostream>
#include"variable.h"
#include"mouse.h"
#include"perspective.h"
#include"Binary.h"
#include"refine.h"
#include"hough.h"
#include"findCar.h"
#include"findCarB.h"
#include"carmove.h"
using namespace cv;
int main()
{
	namedWindow("HistogramF", 1);
	namedWindow("CamShift DemoF", 0);
	setMouseCallback("CamShift DemoF", onMouseF, 0);
	createTrackbar("Vmin", "CamShift DemoF", &vmin, 256, 0);
	createTrackbar("Vmax", "CamShift DemoF", &vmax, 256, 0);
	createTrackbar("Smin", "CamShift DemoF", &smin, 256, 0);
	namedWindow("HistogramB", 1);
	namedWindow("CamShift DemoB", 0);
	setMouseCallback("CamShift DemoB", onMouseB, 0);
	createTrackbar("Vmin", "CamShift DemoB", &vmin, 256, 0);
	createTrackbar("Vmax", "CamShift DemoB", &vmax, 256, 0);
	createTrackbar("Smin", "CamShift DemoB", &smin, 256, 0);
    initializePython();
	while (1)
	{
		capture >> frame;//��ȡ��Ƶ
		namedWindow("originImage");
		imshow("originImage", frame);//��ʾԭ��Ƶ
		Perspective();//͸�ӱ任
		if (!go)
		{
			Binary();//��ֵ��
			//·��ϸ��
			cvThin(50);//�˴����ִ���ϸ������
			HoughTrans(RefineImage);//����任
		}
		else
		{
			findCar();
			cout << "F" << "(" << pointF.x << "," << pointF.y << ")" << "      ";
			findCarB();
			cout << "B" << "(" << pointB.x << "," << pointB.y << ")";
			PointCar = Point2f((pointB.x + pointF.x) / 2, (pointB.y + pointF.y) / 2);
			carmove();
		}
			if (waitKey(30) >= 0)break;
	}

}