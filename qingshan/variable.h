#ifndef VARIABLE_H_INCLUDED
#define VARIABLE_H_INCLUDED

#include<list>
#include<windows.h>
#include"opencv2/opencv.hpp"
#include <opencv2/imgproc/imgproc.hpp>
#include <ctype.h>
#include"car.h"
using namespace cv;
Mat frame, rotated, BinaryImage1, BinaryImage2, BinaryImage3,RefineImage,HoughImage;
Size Myimagesize = Size(500, 500);
VideoCapture capture(0);
Point2f originPoints[4],pointF, pointB, PointCar, Pstart, Pend;
Point2f newPoints[4] = { Point2f(0, 0),Point2f(Myimagesize.width, 0),Point2f(0, Myimagesize.height),Point2f(Myimagesize.width, Myimagesize.height) };
int pointCount[3] = { 0 }, vmin = 10, vmax = 256, smin = 30;;
int nThreshold = 30, nLinemin = 0;
double const mind = 1000;
void Binary();
void on_trackbar(int pos,void *);
void on_trackbar2(int pos, void *);
void cvThin(int intera);
void HoughTrans(Mat &src);
void findCar();
void findCarB();
void carmove();
double Distance(Point2f &a, Point2f &b);
vector<Vec4i> trackLines;
vector<Point2f> AllP;
bool selectObjectF = false, selectObjectB = false, go = false;
int trackObjectF = 0, trackObjectB = 0, pindex;
Point originF, originB;
Rect selectionF, selectionB;
Rect trackWindowF, trackWindowB;
int hsize = 16;
float hranges[] = { 0,180 };
const float* phranges = hranges;
Mat  hsvF, hueF, maskF, histF, histimgF = Mat::zeros(200, 320, CV_8UC3), backprojF;
Mat  hsvB, hueB, maskB, histB, histimgB = Mat::zeros(200, 320, CV_8UC3), backprojB;
bool Going = false;
const double minT = 2;
const double minD = 900;
#endif
