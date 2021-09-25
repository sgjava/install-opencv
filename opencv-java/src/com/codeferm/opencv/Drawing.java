/*
 * Copyright (c) Steven P. Goldsmith. All rights reserved.
 *
 * Created by Steven P. Goldsmith on June 22, 2015
 * sgjava@gmail.com
 */
package com.codeferm.opencv;

import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.LogManager;
import java.util.logging.Logger;

import org.opencv.core.Core;
import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.core.Point;
import org.opencv.core.Scalar;
import org.opencv.core.Size;
import org.opencv.imgcodecs.Imgcodecs;
import org.opencv.imgproc.Imgproc;

/**
 * Example of drawing on Mat and saving to file.
 *
 * args[0] = dest file or will default to "../output/drawing-java.png" if no
 * args passed.
 *
 * @author sgoldsmith
 * @version 1.0.0
 * @since 1.0.0
 */
final class Drawing {
    /**
     * Logger.
     */
    private static final Logger logger = Logger.getLogger(Drawing.class.getName());
    /* Load the OpenCV system library */
    static {
        System.loadLibrary(Core.NATIVE_LIBRARY_NAME);
    }

    /**
     * Suppress default constructor for noninstantiability.
     */
    private Drawing() {
        throw new AssertionError();
    }

    /**
     * Main method.
     *
     * args[0] = source file or will default to "../output/drawing-java.png" if
     * no args passed.
     *
     * @param args
     *            Arguments passed.
     */
    public static void main(final String... args) {
        String outputFile = null;
        // Check how many arguments were passed in
        if (args.length == 0) {
            // If no arguments were passed then default to
            // ../output/drawing-java.png
            outputFile = "../output/drawing-java.png";
        } else {
            outputFile = args[0];
        }
        // Custom logging properties via class loader
        try {
            LogManager.getLogManager()
                    .readConfiguration(Drawing.class.getClassLoader().getResourceAsStream("logging.properties"));
        } catch (SecurityException | IOException e) {
            e.printStackTrace();
        }
        logger.log(Level.INFO, String.format("OpenCV %s", Core.VERSION));
        logger.log(Level.INFO, String.format("Output file: %s", outputFile));
        final var width = 640;
        final var height = 480;
        // Make black image
        final var mat = Mat.zeros(height, width, CvType.CV_8UC3);
        // Create colors
        final var white = new Scalar(255, 255, 255);
        final var blue = new Scalar(255, 0, 0);
        final var green = new Scalar(0, 255, 0);
        final var red = new Scalar(0, 0, 255);
        final var startTime = System.currentTimeMillis();
        // Draw text
        Imgproc.putText(mat, "Java drawing", new Point(10, 30), Imgproc.FONT_HERSHEY_COMPLEX, 1.0, white, 2);
        // Draw line
        Imgproc.line(mat, new Point(width / 2 - 100, height / 2 - 100), new Point(width / 2 + 100, height / 2 + 100),
                white, 2);
        // Draw circle
        Imgproc.circle(mat, new Point(width / 2 - 1, height / 2 - 1), 100, red, 2);
        // Draw ellipse
        Imgproc.ellipse(mat, new Point(width / 2 - 1, height / 2 - 1), new Size(110, 160), 45.0, 0.0, 360.0, blue, 2);
        // Draw rectangle
        Imgproc.rectangle(mat, new Point(width / 2 - 50, height / 2 - 50), new Point(width / 2 + 50, height / 2 + 50),
                blue, 2);
        // Draw filled rectangle
        Imgproc.rectangle(mat, new Point(width / 2 - 40, height / 2 - 40), new Point(width / 2 + 40, height / 2 + 40),
                green, Core.FILLED);
        final var estimatedTime = System.currentTimeMillis() - startTime;
        final var seconds = (double) estimatedTime / 1000;
        logger.log(Level.INFO, String.format("Elapsed time: %4.2f seconds", seconds));
        // Write image file
        Imgcodecs.imwrite(outputFile, mat);
        // Release native memory
        mat.release();
    }
}
