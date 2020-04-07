"""
Copyright (c) Steven P. Goldsmith. All rights reserved.

Created by Steven P. Goldsmith on January 29, 2016
sgjava@gmail.com
"""

"""Motion detector.

Resizes frame, lowers sample rate and uses moving average to determine change
percent. Inner rectangles are filtered out as well. This can result in ~40%
better performance and a more stable ROI.

sys.argv[1] = source file or will default to "../../resources/960x720.mp4" if no args passed.

@author: sgoldsmith

"""

import logging, sys, time, numpy, cv2


def inside(r, q):
    """See if one rectangle inside another"""
    rx, ry, rw, rh = r
    qx, qy, qw, qh = q
    return rx > qx and ry > qy and rx + rw < qx + qw and ry + rh < qy + qh


def contours(source):
    """Return contours"""
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
    outputFile = "../../output/motion-detect-resize-python.avi"
    videoCapture = cv2.VideoCapture(url)
    frameWidth = videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)
    frameHeight = videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    logger.info("OpenCV %s" % cv2.__version__)
    logger.info("Input file: %s" % url)
    logger.info("Output file: %s" % outputFile)
    # Motion detection generally works best with 480 or wider images
    widthDivisor = int(frameWidth / 480)
    if widthDivisor < 1:
        widthDivisor = 1
    frameResizeWidth = int(frameWidth / widthDivisor)
    frameResizeHeight = int(frameHeight / widthDivisor)
    logger.info("Resolution: %dx%d, resized to: %dx%d" % (frameWidth, frameHeight, frameResizeWidth, frameResizeHeight))
    videoWriter = cv2.VideoWriter(outputFile, cv2.VideoWriter_fourcc(*'X264'), videoCapture.get(cv2.CAP_PROP_FPS),
                                  (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))), True)
    # Used for full size image marking
    widthMultiplier = int(frameWidth / frameResizeWidth)
    heightMultiplier = int(frameHeight / frameResizeHeight)     
    # Only check 25% of the frames
    frameToCheck = int(videoCapture.get(cv2.CAP_PROP_FPS) / 4)
    if frameToCheck < 1:
        frameToCheck = 1
    skipCount = 0
    lastFrame = False
    frames = 0
    framesWithMotion = 0
    movingAvgImg = None
    totalPixels = frameResizeWidth * frameResizeHeight
    movementLocations = []
    start = time.time()
    while not lastFrame:
        ret, image = videoCapture.read()
        if ret:
            # Skip frames until count = 0
            if skipCount == 0:
                skipCount = frameToCheck
                # Resize image
                if frameResizeWidth != frameWidth:
                    resizeImg = cv2.resize(image, (frameResizeWidth, frameResizeHeight), interpolation=cv2.INTER_NEAREST)
                else:
                    resizeImg = image                
                # Generate work image by blurring
                workImg = cv2.blur(resizeImg, (8, 8))
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
                movementLocationsFiltered = []
                # Filter out inside rectangles
                for ri, r in enumerate(movementLocations):
                    for qi, q in enumerate(movementLocations):
                        if ri != qi and inside(r, q):
                            break
                    else:
                        movementLocationsFiltered.append(r)
            else:
                skipCount -= 1
            frames += 1
            # Threshold to trigger motion
            if motionPercent > 2.0:
                framesWithMotion += 1
                for x, y, w, h in movementLocationsFiltered:
                    cv2.putText(image, "%dw x %dh" % (w, h), (x * widthMultiplier, (y * heightMultiplier) - 4), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), thickness=2, lineType=cv2.LINE_AA)
                    # Draw rectangle around fond objects
                    cv2.rectangle(image, (x * widthMultiplier, y * heightMultiplier),
                                  ((x + w) * widthMultiplier, (y + h) * heightMultiplier),
                                  (0, 255, 0), 2)
            videoWriter.write(image)
        else:
            lastFrame = True
    elapsed = time.time() - start
    logger.info("%d frames, %d frames with motion" % (frames, framesWithMotion))
    logger.info("%4.1f FPS, elapsed time: %4.2f seconds" % (frames / elapsed, elapsed))
    del videoCapture
    del videoWriter
