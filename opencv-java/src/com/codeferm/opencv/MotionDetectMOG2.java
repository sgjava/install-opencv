/*
 * Copyright (c) Steven P. Goldsmith. All rights reserved.
 *
 * Created by Steven P. Goldsmith on January 10, 2016
 * sgoldsmith@codeferm.com
 */
package com.codeferm.opencv;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.LogManager;
import java.util.logging.Logger;

import org.opencv.core.Core;
import org.opencv.core.Mat;
import org.opencv.core.MatOfPoint;
import org.opencv.core.Point;
import org.opencv.core.Rect;
import org.opencv.core.Scalar;
import org.opencv.core.Size;
import org.opencv.imgproc.Imgproc;
import org.opencv.video.BackgroundSubtractorMOG2;
import org.opencv.video.Video;
import org.opencv.videoio.VideoCapture;
import org.opencv.videoio.VideoWriter;
import org.opencv.videoio.Videoio;

/**
 * Uses Gaussian Mixture-based Background/Foreground Segmentation Algorithm.
 * You'll note this is much slower then using moving average, but motion blobs
 * are more refined.
 *
 * args[0] = source file or will default to "../resources/traffic.mp4" if no
 * args passed.
 *
 * @author sgoldsmith
 * @version 1.0.0
 * @since 1.0.0
 */
final class MotionDetectMOG2 {
    /**
     * Logger.
     */
    private static final Logger logger = Logger.getLogger(MotionDetectMOG2.class.getName());
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
    private MotionDetectMOG2() {
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
            mop.free();
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
        final var outputFile = "../output/motion-detect-mog2-java.avi";
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
            LogManager.getLogManager().readConfiguration(
                    MotionDetectMOG2.class.getClassLoader().getResourceAsStream("logging.properties"));
        } catch (SecurityException | IOException e) {
            e.printStackTrace();
        }
        logger.log(Level.INFO, String.format("OpenCV %s", Core.VERSION));
        logger.log(Level.INFO, String.format("Input file: %s", url));
        logger.log(Level.INFO, String.format("Output file: %s", outputFile));
        final var videoCapture = new VideoCapture();
        videoCapture.open(url);
        final Size frameSize = new Size((int) videoCapture.get(Videoio.CAP_PROP_FRAME_WIDTH),
                (int) videoCapture.get(Videoio.CAP_PROP_FRAME_HEIGHT));
        logger.log(Level.INFO, String.format("Resolution: %s", frameSize));
        final var fourCC = new FourCC("X264");
        final var videoWriter = new VideoWriter(outputFile, fourCC.toInt(),
                videoCapture.get(Videoio.CAP_PROP_FPS), frameSize, true);
        final var mog2 = Video.createBackgroundSubtractorMOG2(300, 32, true);
        final var capture = new Mat();
        final var foreground = new Mat();
        final var blur = new Mat();
        final var binaryImg = new Mat();
        // Create a structuring element (SE)
        final var element = Imgproc.getStructuringElement(Imgproc.MORPH_RECT, new Size(7, 7), new Point(3, 3));
        final var kSize = new Size(4, 4);
        final var rectPoint1 = new Point();
        final var rectPoint2 = new Point();
        final var rectColor = new Scalar(0, 255, 0);
        int frames = 0;
        int framesWithMotion = 0;
        final long startTime = System.currentTimeMillis();
        // Process all frames in file
        while (videoCapture.read(capture)) {
            // Reduce noise with a kernel 4x4
            Imgproc.blur(capture, blur, kSize);
            // Update the background model
            mog2.apply(blur, foreground, -1);
            // Apply the close morphology operation
            Imgproc.morphologyEx(foreground, binaryImg, Imgproc.MORPH_CLOSE, element);
            // Convert to BW
            Imgproc.threshold(binaryImg, binaryImg, 128, 255, Imgproc.THRESH_BINARY);
            final var movementLocations = contours(binaryImg);
            // Contours trigger motion
            if (!movementLocations.isEmpty()) {
                framesWithMotion++;
                for (final Rect rect : movementLocations) {
                    // Filter out smaller blobs
                    if (rect.width > 30 && rect.height > 30) {
                        rectPoint1.x = rect.x;
                        rectPoint1.y = rect.y;
                        rectPoint2.x = rect.x + rect.width;
                        rectPoint2.y = rect.y + rect.height;
                        // Draw rectangle around fond object
                        Imgproc.rectangle(capture, rectPoint1, rectPoint2, rectColor, 2);
                    }
                }
            }
            videoWriter.write(capture);
            frames++;
        }
        final var estimatedTime = System.currentTimeMillis() - startTime;
        final var seconds = (double) estimatedTime / 1000;
        logger.log(Level.INFO, String.format("%d frames, %d frames with motion", frames, framesWithMotion));
        logger.log(Level.INFO, String.format("%4.1f FPS, elapsed time: %4.2f seconds", frames / seconds, seconds));
        // Free native memory
        videoCapture.free();
        videoWriter.free();
        mog2.free();
        capture.free();
        foreground.free();
        blur.free();
        binaryImg.free();
        element.free();
    }
}
