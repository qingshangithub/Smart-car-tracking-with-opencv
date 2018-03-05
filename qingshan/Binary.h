#ifndef BINARY_H_INCLUDED
#define BINARY_H_INCLUDED
#include"variable.h"

void Binary()
{
	BinaryImage1 = getStructuringElement(MORPH_RECT, Size(500, 500));
	BinaryImage2 = getStructuringElement(MORPH_RECT, Size(500, 500));
	BinaryImage3 = getStructuringElement(MORPH_RECT, Size(500, 500));
	namedWindow("Binary");
	cvtColor(rotated, BinaryImage1, CV_BGR2GRAY);
	Mat element = getStructuringElement(MORPH_RECT, Size(5, 5));
	erode(BinaryImage1, BinaryImage2, element);
	createTrackbar("threshold", "Binary", &nThreshold, 255, on_trackbar);
	on_trackbar(0, 0);
	imshow("Binary", BinaryImage3);
}
void on_trackbar(int, void*) {
	threshold(BinaryImage2, BinaryImage3, nThreshold, 255, CV_THRESH_BINARY_INV);
};
#endif