/*
 * Copyright (c) Steven P. Goldsmith. All rights reserved.
 *
 * Created by Steven P. Goldsmith on April 7, 2020
 * sgoldsmith@codeferm.com
 */
package com.codeferm.opencv;

import java.awt.image.BufferedImage;
import java.awt.image.DataBufferByte;
import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.LogManager;
import java.util.logging.Logger;

import org.opencv.core.Core;
import org.opencv.core.Mat;
import org.opencv.highgui.HighGui;
import org.opencv.videoio.VideoCapture;

/**
 * A simple video capture app using highgui.
 *
 * args[0] = camera index, url or will default to "-1" if no args passed.
 *
 * @author sgoldsmith
 * @version 1.0.0
 * @since 1.0.0
 */
final class CaptureHighGui {
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
	private CaptureHighGui() {
		throw new AssertionError();
	}

	/**
	 * Convert from Mat to BufferedImage.
	 *
	 * @param mat Mat array.
	 */
	public static BufferedImage convert(final Mat mat) {
		final var sourcePixels = new byte[mat.width() * mat.height() * mat.channels()];
		mat.get(0, 0, sourcePixels);
		// Create new image and get reference to backing data
		var bufferedImage = new BufferedImage(mat.width(), mat.height(), BufferedImage.TYPE_3BYTE_BGR);
		final var targetPixels = ((DataBufferByte) bufferedImage.getRaster().getDataBuffer()).getData();
		// Fast copy
		System.arraycopy(sourcePixels, 0, targetPixels, 0, sourcePixels.length);
		return bufferedImage;
	}

	/**
	 * Create window and display video.
	 *
	 * args[0] = camera index, url or will default to "0" if no args passed.
	 *
	 * @param args String array of arguments.
	 */
	public static void main(final String... args) {
		String url = null;
		// Check how many arguments were passed in
		if (args.length == 0) {
			// If no arguments were passed then default to camera index -1
			url = "-1";
		} else {
			url = args[0];
		}
		var videoCapture = new VideoCapture();
		// See if URL is an integer: -? = negative sign, could have none or one,
		// \\d+ = one or more digits
		if (url.matches("-?\\d+")) {
			videoCapture = new VideoCapture();
			videoCapture.open(Integer.parseInt(url));
		} else {
			videoCapture = new VideoCapture();
			videoCapture.open(url);
		}
		// Custom logging properties via class loader
		try {
			LogManager.getLogManager()
					.readConfiguration(Canny.class.getClassLoader().getResourceAsStream("logging.properties"));
		} catch (SecurityException | IOException e) {
			e.printStackTrace();
		}
		logger.log(Level.INFO, String.format("OpenCV %s", Core.VERSION));
		logger.log(Level.INFO, "Press [Esc] to exit");
		logger.log(Level.INFO, String.format("URL: %s", url));
		final var mat = new Mat();
		int keyPressed = 0;
		while (keyPressed != 27 && videoCapture.read(mat)) {
			HighGui.imshow("Java Capture", mat);
			keyPressed = HighGui.waitKey(10);
		}
		HighGui.destroyAllWindows();
		// Allow window to close
		HighGui.waitKey(1);
		// Release native memory
		mat.free();
		videoCapture.free();
	}
}
