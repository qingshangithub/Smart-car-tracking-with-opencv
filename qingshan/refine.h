#ifndef REFINE_H_INCLUDED
#define REFINE_H_INCLUDED
#include"variable.h"
void cvThin(int intera)
{
	BinaryImage3.copyTo(RefineImage);
	int i, j, n;
	int width, height;
	width = BinaryImage3.cols - 1;
	//֮���Լ�1���Ƿ��㴦��8���򣬷�ֹԽ��
	height = BinaryImage3.rows - 1;
	int step = BinaryImage3.step;
	int  p2, p3, p4, p5, p6, p7, p8, p9;
	uchar* img;
	bool ifEnd;
	int A1;
	Mat tmpimg;
	//n��ʾ��������
	for (n = 0; n<intera; n++)
	{
		RefineImage.copyTo(tmpimg);
		ifEnd = false;
		img = tmpimg.data;
		for (i = 1; i < height; i++)
		{
			img += step;
			for (j = 1; j<width; j++)
			{
				uchar* p = img + j;
				A1 = 0;
				if (p[0] > 0)
				{
					if (p[-step] == 0 && p[-step + 1]>0) //p2,p3 01ģʽ
					{
						A1++;
					}
					if (p[-step + 1] == 0 && p[1]>0) //p3,p4 01ģʽ
					{
						A1++;
					}
					if (p[1] == 0 && p[step + 1]>0) //p4,p5 01ģʽ
					{
						A1++;
					}
					if (p[step + 1] == 0 && p[step]>0) //p5,p6 01ģʽ
					{
						A1++;
					}
					if (p[step] == 0 && p[step - 1]>0) //p6,p7 01ģʽ
					{
						A1++;
					}
					if (p[step - 1] == 0 && p[-1]>0) //p7,p8 01ģʽ
					{
						A1++;
					}
					if (p[-1] == 0 && p[-step - 1]>0) //p8,p9 01ģʽ
					{
						A1++;
					}
					if (p[-step - 1] == 0 && p[-step]>0) //p9,p2 01ģʽ
					{
						A1++;
					}
					p2 = p[-step]>0 ? 1 : 0;
					p3 = p[-step + 1]>0 ? 1 : 0;
					p4 = p[1]>0 ? 1 : 0;
					p5 = p[step + 1]>0 ? 1 : 0;
					p6 = p[step]>0 ? 1 : 0;
					p7 = p[step - 1]>0 ? 1 : 0;
					p8 = p[-1]>0 ? 1 : 0;
					p9 = p[-step - 1]>0 ? 1 : 0;
					if ((p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9)>1 && (p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9)<7 && A1 == 1)
					{
						if ((p2 == 0 || p4 == 0 || p6 == 0) && (p4 == 0 || p6 == 0 || p8 == 0)) //p2*p4*p6=0 && p4*p6*p8==0
						{
							RefineImage.at<uchar>(i, j) = 0; //����ɾ�����������õ�ǰ����Ϊ0
							ifEnd = true;
						}
					}
				}
			}
		}

		RefineImage.copyTo(tmpimg);
		img = tmpimg.data;
		for (i = 1; i < height; i++)
		{
			img += step;
			for (j = 1; j<width; j++)
			{
				A1 = 0;
				uchar* p = img + j;
				if (p[0] > 0)
				{
					if (p[-step] == 0 && p[-step + 1]>0) //p2,p3 01ģʽ
					{
						A1++;
					}
					if (p[-step + 1] == 0 && p[1]>0) //p3,p4 01ģʽ
					{
						A1++;
					}
					if (p[1] == 0 && p[step + 1]>0) //p4,p5 01ģʽ
					{
						A1++;
					}
					if (p[step + 1] == 0 && p[step]>0) //p5,p6 01ģʽ
					{
						A1++;
					}
					if (p[step] == 0 && p[step - 1]>0) //p6,p7 01ģʽ
					{
						A1++;
					}
					if (p[step - 1] == 0 && p[-1]>0) //p7,p8 01ģʽ
					{
						A1++;
					}
					if (p[-1] == 0 && p[-step - 1]>0) //p8,p9 01ģʽ
					{
						A1++;
					}
					if (p[-step - 1] == 0 && p[-step]>0) //p9,p2 01ģʽ
					{
						A1++;
					}
					p2 = p[-step]>0 ? 1 : 0;
					p3 = p[-step + 1]>0 ? 1 : 0;
					p4 = p[1]>0 ? 1 : 0;
					p5 = p[step + 1]>0 ? 1 : 0;
					p6 = p[step]>0 ? 1 : 0;
					p7 = p[step - 1]>0 ? 1 : 0;
					p8 = p[-1]>0 ? 1 : 0;
					p9 = p[-step - 1]>0 ? 1 : 0;
					if ((p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9)>1 && (p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9)<7 && A1 == 1)
					{
						if ((p2 == 0 || p4 == 0 || p8 == 0) && (p2 == 0 || p6 == 0 || p8 == 0)) //p2*p4*p8=0 && p2*p6*p8==0
						{
							RefineImage.at<uchar>(i, j) = 0; //����ɾ�����������õ�ǰ����Ϊ0
							ifEnd = true;
						}
					}
				}
			}
		}
		imshow("refine",RefineImage);

		//��������ӵ����Ѿ�û�п���ϸ���������ˣ����˳�����
		if (!ifEnd) break;
	}

}

#endif
