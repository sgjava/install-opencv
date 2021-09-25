/*
 * Copyright (c) Steven P. Goldsmith. All rights reserved.
 *
 * Created by Steven P. Goldsmith on January 4, 2013
 * sgjava@gmail.com
 */
package com.codeferm.opencv;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.LogManager;
import java.util.logging.Logger;

import org.opencv.core.Core;
import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.core.MatOfPoint;
import org.opencv.core.Point;
import org.opencv.core.Rect;
import org.opencv.core.Scalar;
import org.opencv.core.Size;
import org.opencv.imgproc.Imgproc;
import org.opencv.videoio.VideoCapture;
import org.opencv.videoio.VideoWriter;
import org.opencv.videoio.Videoio;

/**
 * Uses moving average to determine change percent.
 *
 * args[0] = source file or will default to "../resources/traffic.mp4" if no
 * args passed.
 *
 * @author sgoldsmith
 * @version 1.0.0
 * @since 1.0.0
 */
final class MotionDetect {
    /**
     * Logger.
     */
    private static final Logger logger = Logger.getLogger(MotionDetect.class.getName());
    /* Load the OpenCV system library */
    static {
        System.loadLibrary(Core.NATIVE_LIBRARY_NAME);
    }

    /**
     * Kernel used for contours.
     */
    private static final Mat CONTOUR_KERNEL = Imgproc.getStructuringElement(Imgproc.MORPH_DILATE, new Size(3, 3),
            new Point(1, 1));
    /**
     * Contour hierarchy.
     */
    private static final Mat HIERARCHY = new Mat();
    /**
     * Point used for contour dilate and erode.
     */
    private static final Point CONTOUR_POINT = new Point(-1, -1);

    /**
     * Suppress default constructor for noninstantiability.
     */
    private MotionDetect() {
        throw new AssertionError();
    }

    /**
     * Get contours from image.
     *
     * @param source
     *            Source image.
     * @return List of rectangles.
     */
    public static List<Rect> contours(final Mat source) {
        Imgproc.dilate(source, source, CONTOUR_KERNEL, CONTOUR_POINT, 15);
        Imgproc.erode(source, source, CONTOUR_KERNEL, CONTOUR_POINT, 10);
        final var contoursList = new ArrayList<MatOfPoint>();
        Imgproc.findContours(source, contoursList, HIERARCHY, Imgproc.RETR_TREE, Imgproc.CHAIN_APPROX_SIMPLE);
        final var rectList = new ArrayList<Rect>();
        // Convert MatOfPoint to Rectangles
        for (final var mop : contoursList) {
            rectList.add(Imgproc.boundingRect(mop));
            // Release native memory
            mop.release();
        }
        return rectList;
    }

    /**
     * Mark frames with motion detected.
     *
     * args[0] = source file or will default to "../resources/traffic.mp4" if no
     * args passed.
     *
     * @param args
     *            String array of arguments.
     */
    public static void main(final String... args) {
        String url = null;
        final var outputFile = "../output/motion-detect-java.avi";
        // Check how many arguments were passed in
        if (args.length == 0) {
            // If no arguments were passed then default to
            // ../resources/traffic.mp4
            url = "../resources/traffic.mp4";
        } else {
            url = args[0];
        }
        // Custom logging properties via class loader
        try {
            LogManager.getLogManager()
                    .readConfiguration(MotionDetect.class.getClassLoader().getResourceAsStream("logging.properties"));
        } catch (SecurityException | IOException e) {
            e.printStackTrace();
        }
        logger.log(Level.INFO, String.format("OpenCV %s", Core.VERSION));
        logger.log(Level.INFO, String.format("Input file: %s", url));
        logger.log(Level.INFO, String.format("Output file: %s", outputFile));
        final var videoCapture = new VideoCapture();
        videoCapture.open(url);
        final var frameSize = new Size((int) videoCapture.get(Videoio.CAP_PROP_FRAME_WIDTH),
                (int) videoCapture.get(Videoio.CAP_PROP_FRAME_HEIGHT));
        logger.log(Level.INFO, String.format("Resolution: %s", frameSize));
        final var fourCC = new FourCC("X264");
        final var videoWriter = new VideoWriter(outputFile, fourCC.toInt(),
                videoCapture.get(Videoio.CAP_PROP_FPS), frameSize, true);
        final var mat = new Mat();
        int frames = 0;
        final Mat workImg = new Mat();
        Mat movingAvgImg = null;
        final var gray = new Mat();
        final var diffImg = new Mat();
        final var scaleImg = new Mat();
        final var rectPoint1 = new Point();
        final var rectPoint2 = new Point();
        final var rectColor = new Scalar(0, 255, 0);
        final var kSize = new Size(8, 8);
        final var totalPixels = frameSize.area();
        double motionPercent = 0.0;
        int framesWithMotion = 0;
        final var startTime = System.currentTimeMillis();
        while (videoCapture.read(mat)) {
            // Generate work image by blurring
            Imgproc.blur(mat, workImg, kSize);
            // Generate moving average image if needed
            if (movingAvgImg == null) {
                movingAvgImg = new Mat();
                workImg.convertTo(movingAvgImg, CvType.CV_32F);

            }
            // Generate moving average image
            Imgproc.accumulateWeighted(workImg, movingAvgImg, .03);
            // Convert the scale of the moving average
            Core.convertScaleAbs(movingAvgImg, scaleImg);
            // Subtract the work image frame from the scaled image average
            Core.absdiff(workImg, scaleImg, diffImg);
            // Convert the image to grayscale
            Imgproc.cvtColor(diffImg, gray, Imgproc.COLOR_BGR2GRAY);
            // Convert to BW
            Imgproc.threshold(gray, gray, 25, 255, Imgproc.THRESH_BINARY);
            // Total number of changed motion pixels
            motionPercent = 100.0 * Core.countNonZero(gray) / totalPixels;
            // Detect if camera is adjusting and reset reference if more than
            // 25%
            if (motionPercent > 25.0) {
                workImg.convertTo(movingAvgImg, CvType.CV_32F);
            }
            final var movementLocations = contours(gray);
            // Threshold trigger motion
            if (motionPercent > 0.75) {
                framesWithMotion++;
                for (final Rect rect : movementLocations) {
                    rectPoint1.x = rect.x;
                    rectPoint1.y = rect.y;
                    rectPoint2.x = rect.x + rect.width;
                    rectPoint2.y = rect.y + rect.height;
                    // Draw rectangle around fond object
                    Imgproc.rectangle(mat, rectPoint1, rectPoint2, rectColor, 2);
                }
            }
            videoWriter.write(mat);
            frames++;
        }
        final var estimatedTime = System.currentTimeMillis() - startTime;
        final var seconds = (double) estimatedTime / 1000;
        logger.log(Level.INFO, String.format("%d frames, %d frames with motion", frames, framesWithMotion));
        logger.log(Level.INFO, String.format("%4.1f FPS, elapsed time: %4.2f seconds", frames / seconds, seconds));
        // Free native memory
        videoCapture.release();
        videoWriter.release();
        mat.release();
        workImg.release();
        movingAvgImg.release();
        gray.release();
        diffImg.release();
        scaleImg.release();
    }
}
