#ifndef HOUGH_H_INCLUDED
#define HOOUGH_H_INCLUDED
#include"variable.h"
void HoughTrans(Mat &src)
{
	Mat HoughImage = Mat::zeros(src.size(), CV_8U);
	createTrackbar("linemin", "HOUGH", &nLinemin, 50, on_trackbar2);//通过调节nLinemin的大小来调节霍夫变换中最短检测到的线段长度
	on_trackbar(0, 0);
	for (size_t i = 0; i < trackLines.size(); i++)
	{
		Vec4i l = trackLines[i];
		Vec4i m = trackLines[i + 1];
		line(HoughImage, Point(l[0], l[1]), Point(l[2], l[3]), Scalar(255, 255, 255), 2, CV_AA);
		AllP.push_back(Point2f(l[0], l[1]));
		AllP.push_back(Point2f(l[2], l[3]));
	}
	
    
	
	imshow("HOUGH", HoughImage);
	char c = (char)waitKey(3000);
	if (c==97)go = true;
	for (int i = 0; i < AllP.size(); ++i) { std::cout << "(" << AllP[i].x << "," << AllP[i].y << ")" << "    "; }
}
void on_trackbar2(int, void*) {
	HoughLinesP(RefineImage, trackLines, 1, CV_PI / 180, nLinemin, 10, 10);
};
#endif#
