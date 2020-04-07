/*
 * Copyright (c) Steven P. Goldsmith. All rights reserved.
 *
 * Created by Steven P. Goldsmith on November 5, 2015
 * sgoldsmith@codeferm.com
 */

#include <iostream>
#include <sys/time.h>
#include <opencv2/opencv.hpp>

using namespace std;
using namespace cv;

/**
 * Histogram of Oriented Gradients ([Dalal2005]) object detector.
 *
 * argv[1] = source file or will default to "../../resources/walking.mp4" if no
 * args passed.
 *
 * @author sgoldsmith
 * @version 1.0.0
 * @since 1.0.0
 */
int main(int argc, char *argv[]) {
	int return_val = 0;
	string url = "../../resources/walking.mp4";
	string output_file = "../../output/people-detect-cpp.avi";
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
		int frames_with_people = 0;
		Scalar rect_color = Scalar(0, 255, 0);
		Scalar font_color = Scalar(255, 255, 255);
		Size win_stride = Size(8, 8);
		Size padding = Size(32, 32);
		Point font_point;
		HOGDescriptor hog;
		hog.setSVMDetector(cv::HOGDescriptor::getDefaultPeopleDetector());
		vector<Rect> found_locations;
		vector<double> found_weights;
		char weight[20];
		timeval start_time;
		gettimeofday(&start_time, 0);
		// Process all frames
		while (capture.read(image) && !exit_loop) {
			if (!image.empty()) {
				hog.detectMultiScale(image, found_locations, found_weights, 0.0,
						win_stride, padding, 1.05, 2.0, false);
				if (!found_locations.empty()) {
					frames_with_people++;
					// Mark all found locations
					for (size_t i = 0, max = found_locations.size(); i != max;
							++i) {
						rectangle(image, found_locations[i], rect_color, 2, 8,
								0);
						sprintf(weight, "%1.2f", found_weights[i]);
						font_point.x = found_locations[i].x;
						font_point.y = found_locations[i].y - 4;
						putText(image, weight, font_point, FONT_HERSHEY_PLAIN,
								1.5, font_color, 2, LINE_AA, false);
					}
				}
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
		cout << frames << " frames, " << frames_with_people
				<< " frames with people" << endl;
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
