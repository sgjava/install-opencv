/*
 * Copyright (c) Steven P. Goldsmith. All rights reserved.
 *
 * Created by Steven P. Goldsmith on December 23, 2013
 * sgjava@gmail.com
 */
package com.codeferm.opencv;

import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.LogManager;
import java.util.logging.Logger;

import org.opencv.core.Core;
import org.opencv.core.Mat;
import org.opencv.core.Size;
import org.opencv.imgproc.Imgproc;
import org.opencv.videoio.VideoCapture;
import org.opencv.videoio.VideoWriter;
import org.opencv.videoio.Videoio;

/**
 * Canny Edge Detector.
 *
 * args[0] = source file or will default to "../resources/traffic.mp4" if no
 * args passed.
 *
 * @author sgoldsmith
 * @version 1.0.0
 * @since 1.0.0
 */
final class Canny {
    /**
     * Logger.
     */
    private static final Logger logger = Logger.getLogger(Canny.class.getName());
    /* Load the OpenCV system library */
    static {
        System.loadLibrary(Core.NATIVE_LIBRARY_NAME);
    }

    /**
     * Suppress default constructor for noninstantiability.
     */
    private Canny() {
        throw new AssertionError();
    }

    /**
     * Run Canny edge detection on all frames.
     *
     * args[0] = source file or will default to "../resources/traffic.mp4" if no
     * args passed.
     *
     * @param args
     *            String array of arguments.
     */
    public static void main(final String... args) {
        String url = null;
        final var outputFile = "../output/canny-java.avi";
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
                    .readConfiguration(Canny.class.getClassLoader().getResourceAsStream("logging.properties"));
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
        final var gray = new Mat();
        final var blur = new Mat();
        final var edges = new Mat();
        var dst = new Mat();
        final var kSize = new Size(3, 3);
        final var startTime = System.currentTimeMillis();
        while (videoCapture.read(mat)) {
            // Convert the image to grayscale
            Imgproc.cvtColor(mat, gray, Imgproc.COLOR_BGR2GRAY);
            // Reduce noise with a kernel 3x3
            Imgproc.GaussianBlur(gray, blur, kSize, 0);
            // Canny detector
            Imgproc.Canny(blur, edges, 100, 200, 3, false);
            // Add some colors to edges from original image
            Core.bitwise_and(mat, mat, dst, edges);
            videoWriter.write(dst);
            // This wasn't required in OpenCV 2.4 otherwise you get outline
            // history in video
            dst.free();
            dst = new Mat();
            frames++;
        }
        final var estimatedTime = System.currentTimeMillis() - startTime;
        final var seconds = (double) estimatedTime / 1000;
        logger.log(Level.INFO, String.format("%d frames", frames));
        logger.log(Level.INFO, String.format("%4.1f FPS, elapsed time: %4.2f seconds", frames / seconds, seconds));
        // Release native memory
        videoCapture.free();
        videoWriter.free();
        mat.free();
        gray.free();
        blur.free();
        edges.free();
        dst.free();
    }
}
