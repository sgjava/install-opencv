/*
 * Copyright (c) Steven P. Goldsmith. All rights reserved.
 *
 * Created by Steven P. Goldsmith on November 2, 2015
 * sgoldsmith@codeferm.com
 */

#include <iostream>
#include <opencv2/opencv.hpp>

using namespace std;
using namespace cv;

/**
 * A simple video capture app.
 *
 * argv[1] = camera index, url or will default to "-1" if no args passed.
 *
 * @author sgoldsmith
 * @version 1.0.0
 * @since 1.0.0
 */
int main(int argc, char *argv[]) {
	int return_val = 0;
	cout << CV_VERSION << endl;
	cout << "Press [Esc] to exit" << endl;
	VideoCapture capture;
	Mat frame;
	// See if URL arg passed
	if (argc == 2) {
		char *end;
		long l = strtol(argv[1], &end, 10);
		// See if long conversion worked
		if (end != argv[1] || *end == '\0') {
			// Use number version
			cout << "URL: " << l << endl;
			capture.open(l);
		} else {
			// Use string version
			cout << "URL: " << argv[1] << endl;
			capture.open(argv[1]);
		}
	} else {
		// Use default device
		cout << "URL: -1" << endl;
		capture.open(-1);
	}
	// See if video capture opened
	if (capture.isOpened()) {
		cout << "Resolution: " << capture.get(CAP_PROP_FRAME_WIDTH) << "x"
				<< capture.get(CAP_PROP_FRAME_HEIGHT) << endl;
		bool exit_loop = false;
		// Display frames until escape pressed
		while (capture.read(frame) && !exit_loop) {
			if (!frame.empty()) {
				imshow("C++ Capture", frame);
				int c = waitKey(10);
				// Wait for escape
				if ((char) c == 27) {
					exit_loop = true;
				}
			} else {
				cout << "No frame captured" << endl;
				exit_loop = true;
			}
		}
		// Release VideoCapture
		capture.release();
	} else {
		cout << "Unable to open device" << endl;
		return_val = -1;
	}
	return return_val;
}
