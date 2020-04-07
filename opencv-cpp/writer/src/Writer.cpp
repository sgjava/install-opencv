/*
 * Copyright (c) Steven P. Goldsmith. All rights reserved.
 *
 * Created by Steven P. Goldsmith on November 5, 2015
 * sgjava@gmail.com
 */

#include <iostream>
#include <sys/time.h>
#include <opencv2/opencv.hpp>

using namespace std;
using namespace cv;

/**
 * Write video file.
 *
 * argv[1] = source file or will default to "../../resources/traffic.mp4" if no
 * args passed.
 *
 * @author sgoldsmith
 * @version 1.0.0
 * @since 1.0.0
 */
int main(int argc, char *argv[]) {
	int return_val = 0;
	string url = "../../resources/traffic.mp4";
	string output_file = "../../output/writer-cpp.avi";
	cout << CV_VERSION << endl;
	cout << "Press [Esc] to exit" << endl;
	VideoCapture capture;
	Mat image;
	// See if URL arg passed
	if (argc == 2) {
		url = argv[1];
	}
	cout << "Input file:" << url << endl;
	cout << "Output file:" << output_file << endl;
	capture.open(url);
	// See if video capture opened
	if (capture.isOpened()) {
		cout << "Resolution: " << capture.get(CAP_PROP_FRAME_WIDTH) << "x"
				<< capture.get(CAP_PROP_FRAME_HEIGHT) << endl;
		bool exit_loop = false;
		// Video writer
		VideoWriter writer(output_file, (int) capture.get(CAP_PROP_FOURCC),
				(int) capture.get(CAP_PROP_FPS),
				Size((int) capture.get(CAP_PROP_FRAME_WIDTH),
						(int) capture.get(CAP_PROP_FRAME_HEIGHT)));
		int frames = 0;
		timeval start_time;
		gettimeofday(&start_time, 0);
		// Process all frames
		while (capture.read(image) && !exit_loop) {
			if (!image.empty()) {
				// Write frame
				writer.write(image);
				frames++;
			} else {
				cout << "No frame captured" << endl;
				exit_loop = true;
			}
		}
		timeval end_time;
		gettimeofday(&end_time, 0);
		cout << frames << " frames" << endl;
		cout << "FPS " << (frames / (end_time.tv_sec - start_time.tv_sec))
				<< ", elapsed time: " << (end_time.tv_sec - start_time.tv_sec)
				<< " seconds" << endl;
		// Release VideoWriter
		writer.release();
		// Release VideoCapture
		capture.release();
	} else {
		cout << "Unable to open device" << endl;
		return_val = -1;
	}
	return return_val;
}
