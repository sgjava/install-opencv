/*
 * Copyright (c) Steven P. Goldsmith. All rights reserved.
 *
 * Created by Steven P. Goldsmith on November 6, 2015
 * sgoldsmith@codeferm.com
 */

#include <glob.h>
#include <iostream>
#include <sys/time.h>
#include <sstream>
#include <vector>
#include <opencv2/opencv.hpp>

using namespace std;
using namespace cv;

/**
 * Set the criteria for the cornerSubPix algorithm.
 */
static const TermCriteria CRITERIA = TermCriteria(
		TermCriteria::EPS + TermCriteria::COUNT, 30, 0.1);

/** @brief Returns list of file names.

 @param pattern Mask to match.

 Return vector of sting containing list of files names matching pattern.
 */
vector<string> globVector(const string& pattern) {
	glob_t glob_result;
	glob(pattern.c_str(), GLOB_TILDE, NULL, &glob_result);
	vector<string> files;
	for (unsigned int i = 0; i < glob_result.gl_pathc; ++i) {
		files.push_back(string(glob_result.gl_pathv[i]));
	}
	globfree(&glob_result);
	return files;
}

/** @brief Find chess board corners.

 @param gray Source chessboard view. It must be an 8-bit grayscale or color image.
 @param pattern_size Number of inner corners per a chessboard row and column.
 @param win_size Half of the side length of the search window.

 The function attempts to determine whether the input image is a view of the chessboard pattern and
 locate the internal chessboard corners. The function returns a non-zero value if all of the corners
 are found and they are placed in a certain order (row by row, left to right in every row).
 Otherwise, if the function fails to find all the corners or reorder them, it returns 0. For example,
 a regular chessboard has 8 x 8 squares and 7 x 7 internal corners, that is, points where the black
 squares touch each other. The detected coordinates are approximate, and to determine their positions
 more accurately, the function calls cornerSubPix. You also may use the function cornerSubPix with
 different parameters if returned coordinates are not accurate enough.
 */
vector<Point2f> getCorners(Mat gray, Size pattern_size, Size win_size,
		Size zone_size) {
	vector<Point2f> corners;
	if (findChessboardCorners(gray, pattern_size, corners)) {
		cornerSubPix(gray, corners, win_size, zone_size, CRITERIA);
	}
	return corners;
}

/** @brief Point3f corners.

 @param pattern_size Pattern size.
 */
vector<Point3f> getCorner3f(Size pattern_size) {
	vector<Point3f> corners3f(pattern_size.height * pattern_size.width);
	double squareSize = 50;
	int cnt = 0;
	for (int i = 0; i < pattern_size.height; ++i) {
		for (int j = 0; j < pattern_size.width; ++j, cnt++) {
			corners3f[cnt] = Point3f(j * squareSize, i * squareSize, 0.0);
		}
	}
	return corners3f;
}

/** @brief Calculate re-projection error.

 @param object_points Vector of vectors of calibration pattern points.
 @param rvecs Vector of rotation vectors.
 @param tvecs Vector of translation vectors estimated for each pattern view.
 @param camera_matrix 3x3 floating-point camera matrix.
 @param dist_coeffs Vector of distortion coefficients.
 @param image_points Vector of vectors of the projections of calibration pattern points.

 Re-projection error gives a good estimation of just how exact the found parameters are. This
 should be as close to zero as possible.

 The function computes projections of 3D points to the image plane given intrinsic and extrinsic
 camera parameters. Optionally, the function computes Jacobians - matrices of partial derivatives of
 image points coordinates (as functions of all the input parameters) with respect to the particular
 parameters, intrinsic and/or extrinsic. The Jacobians are used during the global optimization in
 calibrateCamera, solvePnP, and stereoCalibrate . The function itself can also be used to compute a
 re-projection error given the current intrinsic and extrinsic parameters.

 @note By setting rvec=tvec=(0,0,0) or by setting cameraMatrix to a 3x3 identity matrix, or by
 passing zero distortion coefficients, you can get various useful partial cases of the function. This
 means that you can compute the distorted coordinates for a sparse set of points or apply a
 perspective transformation (and also compute the derivatives) in the ideal zero-distortion setup.
 */
double reprojectionError(vector<vector<Point3f> > object_points,
		vector<Mat> rvecs, vector<Mat> tvecs, Mat camera_matrix,
		Mat dist_coeffs, vector<vector<Point2f> > image_points) {
	double total_error = 0;
	double total_points = 0;
	vector<Point2f> corners_projected;
	for (size_t i = 0, max = object_points.size(); i != max; ++i) {
		projectPoints(object_points[i], rvecs[i], tvecs[i], camera_matrix,
				dist_coeffs, corners_projected);
		double error = norm(image_points[i], corners_projected, NORM_L2);
		int n = object_points[i].size();
		total_error += error * error;
		total_points += n;
	}
	return sqrt(total_error / total_points);
}

/** @brief Calibrate camera.

 @param object_points Vector of vectors of calibration pattern points.
 @param image_points Vector of vectors of the projections of calibration pattern points.
 @param images Vector of images to use in calibration.

 The function estimates the intrinsic camera parameters and extrinsic parameters for each of the
 views. The algorithm is based on @cite Zhang2000 and @cite BouguetMCT . The coordinates of 3D object
 points and their corresponding 2D projections in each view must be specified. That may be achieved
 by using an object with a known geometry and easily detectable feature points. Such an object is
 called a calibration rig or calibration pattern, and OpenCV has built-in support for a chessboard as
 a calibration rig (see findChessboardCorners ). Currently, initialization of intrinsic parameters
 (when CV_CALIB_USE_INTRINSIC_GUESS is not set) is only implemented for planar calibration
 patterns (where Z-coordinates of the object points must be all zeros). 3D calibration rigs can also
 be used as long as initial cameraMatrix is provided.
 */
pair<Mat, Mat> calibrate(vector<vector<Point3f> > object_points,
		vector<vector<Point2f> > image_points, vector<Mat> images) {
	vector<Mat> rvecs, tvecs;
	Mat camera_matrix(3, 3, CV_64F);
	Mat dist_coeffs(8, 1, CV_64F);
	double rms = calibrateCamera(object_points, image_points, images[0].size(),
			camera_matrix, dist_coeffs, rvecs, tvecs);
	double error = reprojectionError(object_points, rvecs, tvecs, camera_matrix,
			dist_coeffs, image_points);
	cout << "Mean reprojection error: " << error << endl;
	cout << "RMS: " << rms << endl;
	cout << "Camera matrix: " << camera_matrix << endl;
	cout << "Distortion coefficients: " << dist_coeffs << endl;
	pair<Mat, Mat> ret_params(camera_matrix, dist_coeffs);
	return ret_params;
}

/** @brief Undistort image.

 @param image Image to undistort.
 @param camera_matrix 3x3 floating-point camera matrix.
 @param dist_coeffs Vector of distortion coefficients.

 The function computes and returns the optimal new camera matrix based on the free scaling parameter.
 By varying this parameter, you may retrieve only sensible pixels alpha=0 , keep all the original
 image pixels if there is valuable information in the corners alpha=1 , or get something in between.
 When alpha\>0 , the undistortion result is likely to have some black pixels corresponding to
 "virtual" pixels outside of the captured distorted image. The original camera matrix, distortion
 coefficients, the computed new camera matrix, and newImageSize should be passed to
 initUndistortRectifyMap to produce the maps for remap.
 */
Mat undistort(Mat image, Mat camera_matrix, Mat dist_coeffs) {
	Mat new_camera_mtx = getOptimalNewCameraMatrix(camera_matrix, dist_coeffs,
			image.size(), 0);
	Mat mat;
	undistort(image, mat, camera_matrix, dist_coeffs, new_camera_mtx);
	return mat;
}

/** @brief Undistort files matching file mask.

 @param in_mask File mask used to select files.
 @param out_dir Where undistorted images are stored..
 @param camera_matrix 3x3 floating-point camera matrix.
 @param dist_coeffs Vector of distortion coefficients.

 Process all images matching in_mask and output undistorted images to out_dir.

 */
void undistortAll(string in_mask, string out_dir, Mat camera_matrix,
		Mat dist_coeffs) {
	// Get list of files to process.
	vector<string> files = globVector(in_mask);
	for (size_t i = 0, max = files.size(); i != max; ++i) {
		// Read in image unchanged
		Mat mat = imread(files[i], IMREAD_UNCHANGED);
		Mat undistort_img = undistort(mat, camera_matrix, dist_coeffs);
		// Get just file name from path
		string just_file_name = files[i].substr(files[i].find_last_of("/") + 1,
				files[i].length());
		// File name to write to
		string write_file_name = out_dir
				+ just_file_name.substr(0, just_file_name.find_last_of("."))
				+ "-cpp-undistort.bmp";
		imwrite(write_file_name, undistort_img);
	}
}

/** @brief Get object and image points for files matching file mask.

 @param in_mask File mask used to select files.
 @param out_dir Where undistorted images are stored.
 @param pattern_size Number of inner corners per a chessboard row and column.

 Process all images matching in_mask and build object and image point vectors.

 */
pair<Mat, Mat> getPoints(string in_mask, string out_dir, Size pattern_size) {
	vector<Point3f> corners3f = getCorner3f(pattern_size);
	// Get list of files to process.
	vector<string> files = globVector(in_mask);
	vector<vector<Point3f> > object_points(files.size());
	vector<vector<Point2f> > image_points(files.size());
	vector<Mat> images(files.size());
	int passed = 0;
	for (size_t i = 0, max = files.size(); i != max; ++i) {
		Mat mat = imread(files[i], IMREAD_GRAYSCALE);
		vector<Point2f> corners;
		Size win_size = Size(5, 5);
		Size zone_size = Size(-1, -1);
		corners = getCorners(mat, pattern_size, win_size, zone_size);
		// Process only images that pass getCorners
		if (!corners.empty()) {
			Mat vis;
			// Convert to color for drawing
			cvtColor(mat, vis, COLOR_GRAY2BGR);
			drawChessboardCorners(vis, pattern_size, corners, true);
			// Get just file name from path
			string just_file_name = files[i].substr(
					files[i].find_last_of("/") + 1, files[i].length());
			// File name to write to
			string write_file_name = out_dir
					+ just_file_name.substr(0, just_file_name.find_last_of("."))
					+ "-cpp.bmp";
			imwrite(write_file_name, vis);
			object_points[i] = corners3f;
			image_points[i] = corners;
			images[i] = mat;
			passed++;
		} else {
			cout << "Chessboard not found in: " << files[i] << endl;
		}
	}
	cout << "Images passed findChessboardCorners: " << passed << endl;
	// Calibrate camera
	return calibrate(object_points, image_points, images);
}

/** @brief Save Mat to file.

 @param mat Mat to save.
 @param file_name File name to save as.
 */
void saveMat(Mat mat, string file_name) {
	FileStorage file(file_name, FileStorage::WRITE);
	file << "mat" << mat;
	file.release();
}

/** @brief Load mat from file.

 @param file_name File name to load.
 */
Mat loadMat(string file_name) {
	FileStorage file(file_name, FileStorage::READ);
	Mat mat;
	file["mat"] >> mat;
	file.release();
	return mat;
}

/**
 * Camera calibration.
 *
 * You need at least 10 images that pass cv2.findChessboardCorners at varying
 * angles and distances from the camera. You must do this for each resolution
 * you wish to calibrate. Camera matrix and distortion coefficients are written
 * to files for later use with undistort. This code is based on
 * http://computervisionandjava.blogspot.com/2013/10/camera-cailbration.html,
 * but follows Python code closely (hence the identical values returned).
 *
 * argv[1] = input file mask or will default to "../../resources/2015*.jpg" if no
 * args passed.
 *
 * argv[2] = output dir or will default to "../../output/" if no args passed.
 *
 * argv[3]] = cols,rows of chess board or will default to "7,5" if no args
 * passed.
 *
 * @author sgoldsmith
 * @version 1.0.0
 * @since 1.0.0
 */
int main(int argc, char *argv[]) {
	cout << CV_VERSION << endl;
	int return_val = 0;
	string in_mask;
	string out_dir;
	Size pattern_size;
	// Parse args
	if (argc == 4) {
		in_mask = argv[1];
		out_dir = argv[2];
		stringstream ss(argv[3]);
		vector<int> result(2);
		int i = 0;
		// Parse width and height "7,5" for example
		while (ss.good()) {
			string substr;
			getline(ss, substr, ',');
			result[i++] = atoi(substr.c_str());
		}
		pattern_size = Size(result[0], result[1]);
	} else {
		in_mask = "../../resources/2015*.jpg";
		out_dir = "../../output/";
		pattern_size = Size(7, 5);
	}
	cout << "Input mask: " << in_mask << endl;
	cout << "Output dir: " << out_dir << endl;
	cout << "Pattern size: " << pattern_size << endl;
	timeval start_time;
	gettimeofday(&start_time, 0);
	pair<Mat, Mat> data = getPoints(in_mask, out_dir, pattern_size);
	undistortAll(in_mask, out_dir, data.first, data.second);
	// Save mats
	cout << "Saving calibration parameters to file" << endl;
	saveMat(data.first, out_dir + "camera-matrix.xml");
	saveMat(data.second, out_dir + "dist-coefs.xml");
	// Load mats
	cout << "Restoring calibration parameters from file" << endl;
	Mat camera_matrix =loadMat(out_dir + "camera-matrix.xml");
	Mat dist_coeffs	= loadMat(out_dir + "dist-coefs.xml");
	cout << "Camera matrix: " << camera_matrix << endl;
	cout << "Distortion coefficients: " << dist_coeffs << endl;
	timeval end_time;
	gettimeofday(&end_time, 0);
	cout << "Elapsed time: " << (end_time.tv_sec - start_time.tv_sec)
			<< " seconds" << endl;
	return return_val;
}
