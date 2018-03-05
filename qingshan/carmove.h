#ifndef CARMOVE_H_INCLUDED
#define CARMOVE_H_INCLUDED
#include"variable.h"
#include<cmath>
double Distance(Point2f &A, Point2f &B)
{
	double x = abs(A.x - B.x);
	double y = abs(A.y - B.y);
	double d = x * x + y * y;
	return d;
}

void carmove()    
{
	if (AllP.size() != 0)
	{
		int sum = trackLines.size();
		double th, d;
		if (Going == false)
		{

			for (int i = 0; i < AllP.size(); ++i)
			{
				double dd = Distance(PointCar, AllP[i]);
				if (i == 0)
				{
					pindex = i;
					d = dd;
				}
				else if (dd <= d)
				{
					pindex = i;
					d = dd;
				}
			}
			Pstart = PointCar;
			Pend = AllP[pindex];
		}
		Going = true;
		if (Distance(PointCar, Pend) <= minD)
		{
			Going = false;
			AllP.erase(AllP.begin() + pindex);
			return;
		}
		double tant1 = (pointB.y - pointF.y) / (pointB.x - pointF.x);
		double tant2 = (Pend.y - PointCar.y) / (Pend.x - PointCar.x);
		int flag = (pointB.x - pointF.x)*(Pend.x - PointCar.x) + (Pend.y - PointCar.y)*(pointB.y - pointF.y) > 0 ? 1 : -1;
		double tant3 = (tant1 - tant2) / (1 + tant1*tant2) * flag;
		cout << tant3;
		if (tant3 > minT)
		{


			setTurnBias(-2);  //左转
			std::cout << "左转";
			waitKey(300);
			stop();
			waitKey(2000);
		}
		else if (tant3 < -1 * minT)
		{

			setTurnBias(2);  //右转
			std::cout << "右转";
			waitKey(300);
			stop();
			waitKey(2000);
		}
		else
		{
			setTurnBias(0);  //前进
			setStraightSpeed(-3);
			std::cout << "直";
			waitKey(300);
			stop();
			waitKey(2000);
		}
	}

	
}
#endif