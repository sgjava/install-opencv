/*
 * Copyright (c) Steven P. Goldsmith. All rights reserved.
 *
 * Created by Steven P. Goldsmith on November 8, 2015
 * sgoldsmith@codeferm.com
 */

#include <iostream>
#include <sys/time.h>
#include <opencv2/opencv.hpp>

using namespace std;
using namespace cv;

/**
 * Example of drawing on Mat and saving to file.
 *
 * argv[1] = dest file or will default to "../../output/drawing-cpp.png" if no args
 * passed.
 *
 * @author sgoldsmith
 * @version 1.0.0
 * @since 1.0.0
 */
int main(int argc, char *argv[]) {
	int return_val = 0;
	string output_file = "../../output/drawing-cpp.png";
	cout << CV_VERSION << endl;
	// See if output file name arg passed
	if (argc == 2) {
		output_file = argv[1];
	}
	cout << "Output file: " << output_file << endl;
	int width = 640;
	int height = 480;
	// Make black image
	Mat mat = Mat::zeros(height, width, CV_8UC3);
	// Create colors
	Scalar white = Scalar(255, 255, 255);
	Scalar blue = Scalar(255, 0, 0);
	Scalar green = Scalar(0, 255, 0);
	Scalar red = Scalar(0, 0, 255);
	timeval start_time;
	gettimeofday(&start_time, 0);
	// Draw text
	putText(mat, "C++ drawing", Point(10, 30), FONT_HERSHEY_COMPLEX, 1.0, white,
			2);
	// Draw line
	line(mat, Point(width / 2 - 100, height / 2 - 100),
			Point(width / 2 + 100, height / 2 + 100), white, 2);
	// Draw circle
	circle(mat, Point(width / 2 - 1, height / 2 - 1), 100, red, 2);
	// Draw ellipse
	ellipse(mat, Point(width / 2 - 1, height / 2 - 1), Size(110, 160), 45.0,
			0.0, 360.0, blue, 2);
	// Draw rectangle
	rectangle(mat, Point(width / 2 - 50, height / 2 - 50),
			Point(width / 2 + 50, height / 2 + 50), blue, 2);
	// Draw filled rectangle
	rectangle(mat, Point(width / 2 - 40, height / 2 - 40),
			Point(width / 2 + 40, height / 2 + 40), green, FILLED);
	// Write image file
	imwrite(output_file, mat);
	timeval end_time;
	gettimeofday(&end_time, 0);
	cout << "Elapsed time: " << (end_time.tv_sec - start_time.tv_sec)
			<< " seconds" << endl;
	return return_val;
}
