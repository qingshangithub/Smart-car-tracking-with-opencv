#ifndef	FINDCAR_H_INCLUDED
#define FINDCAR_H_INCLUDED
#include"variable.h"
#include "opencv2/highgui/highgui.hpp"

#include <iostream>
#include <ctype.h>

using namespace cv;
using namespace std;

static void onMouseF(int event, int x, int y, int, void*)
{
	if (selectObjectF)
	{
		selectionF.x = MIN(x, originF.x);
		selectionF.y = MIN(y, originF.y);
		selectionF.width = std::abs(x - originF.x);
		selectionF.height = std::abs(y - originF.y);

		selectionF &= Rect(0, 0, rotated.cols, rotated.rows);
	}

	switch (event)
	{
	case CV_EVENT_LBUTTONDOWN:
		originF = Point(x, y);
		selectionF = Rect(x, y, 0, 0);
		selectObjectF = true;
		break;
	case CV_EVENT_LBUTTONUP:
		selectObjectF = false;
		if (selectionF.width > 0 && selectionF.height > 0)
			trackObjectF = -1;
		break;
	}
}

void findCar()
{
		
		cvtColor(rotated, hsvF, COLOR_BGR2HSV);

		if (trackObjectF)
		{
			int _vmin = vmin, _vmax = vmax;

			inRange(hsvF, Scalar(0, smin, MIN(_vmin, _vmax)),
				Scalar(180, 256, MAX(_vmin, _vmax)), maskF);
			int ch[] = { 0, 0 };
			hueF.create(hsvF.size(), hsvF.depth());
			mixChannels(&hsvF, 1, &hueF, 1, ch, 1);

			if (trackObjectF < 0)
			{
				Mat roi(hueF, selectionF), maskroi(maskF, selectionF);
				calcHist(&roi, 1, 0, maskroi, histF, 1, &hsize, &phranges);
				normalize(histF, histF, 0, 255, CV_MINMAX);

				trackWindowF= selectionF;
				trackObjectF = 1;

				histimgF = Scalar::all(0);
				int binW = histimgF.cols / hsize;
				Mat buf(1, hsize, CV_8UC3);
				for (int i = 0; i < hsize; i++)
					buf.at<Vec3b>(i) = Vec3b(saturate_cast<uchar>(i*180. / hsize), 255, 255);
				cvtColor(buf, buf, CV_HSV2BGR);

				for (int i = 0; i < hsize; i++)
				{
					int val = saturate_cast<int>(histF.at<float>(i)*histimgF.rows / 255);
					rectangle(histimgF, Point(i*binW, histimgF.rows),
						Point((i + 1)*binW, histimgF.rows - val),
						Scalar(buf.at<Vec3b>(i)), -1, 8);
				}
			}

			calcBackProject(&hueF, 1, 0, histF, backprojF, &phranges);
			backprojF &= maskF;
			RotatedRect trackBox = CamShift(backprojF, trackWindowF,
				TermCriteria(CV_TERMCRIT_EPS | CV_TERMCRIT_ITER, 10, 1));
			if (trackWindowF.area() <= 1)
			{
				int cols = backprojF.cols, rows = backprojF.rows, r = (MIN(cols, rows) + 5) / 6;
				trackWindowF = Rect(trackWindowF.x - r, trackWindowF.y - r,
					trackWindowF.x + r, trackWindowF.y + r) &
					Rect(0, 0, cols, rows);
			}
			ellipse(rotated, trackBox, Scalar(0, 0, 255), 3, CV_AA);
			pointF = trackBox.center;
		}


		if (selectObjectF && selectionF.width > 0 && selectionF.height > 0)
		{
			Mat roi(rotated, selectionF);
			bitwise_not(roi, roi);
		}
		imshow("CamShift DemoF", rotated);
		imshow("HistogramF", histimgF);
}
#endif