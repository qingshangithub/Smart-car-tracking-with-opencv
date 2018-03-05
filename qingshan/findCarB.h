#ifndef	FINDCARB_H_INCLUDED
#define FINDCARB_H_INCLUDED
#include"variable.h"
#include "opencv2/highgui/highgui.hpp"

#include <iostream>
#include <ctype.h>

using namespace cv;
using namespace std;

static void onMouseB(int event, int x, int y, int, void*)
{
	if (selectObjectB)
	{
		selectionB.x = MIN(x, originB.x);
		selectionB.y = MIN(y, originB.y);
		selectionB.width = std::abs(x - originB.x);
		selectionB.height = std::abs(y - originB.y);

		selectionB &= Rect(0, 0, rotated.cols, rotated.rows);
	}

	switch (event)
	{
	case CV_EVENT_LBUTTONDOWN:
		originB = Point(x, y);
		selectionB = Rect(x, y, 0, 0);
		selectObjectB = true;
		break;
	case CV_EVENT_LBUTTONUP:
		selectObjectB = false;
		if (selectionB.width > 0 && selectionB.height > 0)
			trackObjectB = -1;
		break;
	}
}

void findCarB()
{

	cvtColor(rotated, hsvB, COLOR_BGR2HSV);

	if (trackObjectB)
	{
		int _vmin = vmin, _vmax = vmax;

		inRange(hsvB, Scalar(0, smin, MIN(_vmin, _vmax)),
			Scalar(180, 256, MAX(_vmin, _vmax)), maskB);
		int ch[] = { 0, 0 };
		hueB.create(hsvB.size(), hsvB.depth());
		mixChannels(&hsvB, 1, &hueB, 1, ch, 1);
		
		if (trackObjectB < 0)
		{
			Mat roi(hueB, selectionB), maskroi(maskB, selectionB);
			calcHist(&roi, 1, 0, maskroi, histB, 1, &hsize, &phranges);
			normalize(histB, histB, 0, 255, CV_MINMAX);

			trackWindowB = selectionB;
			trackObjectB = 1;

			histimgB = Scalar::all(0);
			int binW = histimgB.cols / hsize;
			Mat buf(1, hsize, CV_8UC3);
			for (int i = 0; i < hsize; i++)
				buf.at<Vec3b>(i) = Vec3b(saturate_cast<uchar>(i*180. / hsize), 255, 255);
			cvtColor(buf, buf, CV_HSV2BGR);

			for (int i = 0; i < hsize; i++)
			{
				int val = saturate_cast<int>(histB.at<float>(i)*histimgB.rows / 255);
				rectangle(histimgB, Point(i*binW, histimgB.rows),
					Point((i + 1)*binW, histimgB.rows - val),
					Scalar(buf.at<Vec3b>(i)), -1, 8);
			}
		}

		calcBackProject(&hueB, 1, 0, histB, backprojB, &phranges);
		backprojB &= maskB;
		RotatedRect trackBox = CamShift(backprojB, trackWindowB,
			TermCriteria(CV_TERMCRIT_EPS | CV_TERMCRIT_ITER, 10, 1));
		if (trackWindowB.area() <= 1)
		{
			int cols = backprojB.cols, rows = backprojB.rows, r = (MIN(cols, rows) + 5) / 6;
			trackWindowB = Rect(trackWindowB.x - r, trackWindowB.y - r,
				trackWindowB.x + r, trackWindowB.y + r) &
				Rect(0, 0, cols, rows);
		}
		ellipse(rotated, trackBox, Scalar(0, 0, 255), 3, CV_AA);
		pointB = trackBox.center;
	}


	if (selectObjectB && selectionB.width > 0 && selectionB.height > 0)
	{
		Mat roi(rotated, selectionB);
		bitwise_not(roi, roi);
	}

	imshow("CamShift DemoB", rotated);
	imshow("HistogramB", histimgB);
}
#endif