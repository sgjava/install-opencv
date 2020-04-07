"""
Copyright (c) Steven P. Goldsmith. All rights reserved.

Created by Steven P. Goldsmith on December 23, 2013
sgjava@gmail.com
"""

"""Motion detector.
    
Uses moving average to determine change percent.

sys.argv[1] = source file or will default to "../../resources/960x720.mp4" if no args passed.

@author: sgoldsmith

"""

import logging, sys, time, numpy, cv2


def contours(source):
    # The background (bright) dilates around the black regions of frame
    source = cv2.dilate(source, None, iterations=15);
    # The bright areas of the image (the background, apparently), get thinner, whereas the dark zones bigger
    source = cv2.erode(source, None, iterations=10);
    # Find contours
    contours, _ = cv2.findContours(source, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2:]
    # Add objects with motion
    movementLocations = []
    for contour in contours:
        rect = cv2.boundingRect(contour)
        movementLocations.append(rect)
    return movementLocations


if __name__ == '__main__':
    # Configure logger
    logger = logging.getLogger("MotionDetect")
    logger.setLevel("INFO")
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(module)s %(message)s")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # If no args passed then default to internal file
    if len(sys.argv) < 2:
        url = "../../resources/traffic.mp4"
    else:
        url = sys.argv[1]
    outputFile = "../../output/motion-detect-python.avi"
    videoCapture = cv2.VideoCapture(url)
    logger.info("OpenCV %s" % cv2.__version__)
    logger.info("Input file: %s" % url)
    logger.info("Output file: %s" % outputFile)
    logger.info("Resolution: %dx%d" % (videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH),
                                   videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    videoWriter = cv2.VideoWriter(outputFile, cv2.VideoWriter_fourcc(*'X264'), videoCapture.get(cv2.CAP_PROP_FPS),
                                  (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))), True)
    lastFrame = False
    frames = 0
    framesWithMotion = 0
    movingAvgImg = None
    totalPixels = videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH) * videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    movementLocations = []
    start = time.time()
    while not lastFrame:
        ret, image = videoCapture.read()
        if ret:
            # Generate work image by blurring
            workImg = cv2.blur(image, (8, 8))
            # Generate moving average image if needed
            if movingAvgImg is None:
                movingAvgImg = numpy.float32(workImg)
            # Generate moving average image
            cv2.accumulateWeighted(workImg, movingAvgImg, .03)
            diffImg = cv2.absdiff(workImg, cv2.convertScaleAbs(movingAvgImg))
            # Convert to grayscale
            grayImg = cv2.cvtColor(diffImg, cv2.COLOR_BGR2GRAY)
            # Convert to BW
            return_val, grayImg = cv2.threshold(grayImg, 25, 255, cv2.THRESH_BINARY)
            # Total number of changed motion pixels
            motionPercent = 100.0 * cv2.countNonZero(grayImg) / totalPixels
            # Detect if camera is adjusting and reset reference if more than maxChange
            if motionPercent > 25.0:
                movingAvgImg = numpy.float32(workImg)
            movementLocations = contours(grayImg)
            # Threshold trigger motion
            if motionPercent > 0.5:
                framesWithMotion += 1
                for x, y, w, h in movementLocations:
                    # Draw rectangle around fond object
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            videoWriter.write(image)
            frames += 1
        else:
            lastFrame = True
    elapsed = time.time() - start
    logger.info("%d frames, %d frames with motion" % (frames, framesWithMotion))
    logger.info("%4.1f FPS, elapsed time: %4.2f seconds" % (frames / elapsed, elapsed))
    del videoCapture
    del videoWriter
