"""
Copyright (c) Steven P. Goldsmith. All rights reserved.

Created by Steven P. Goldsmith on January 29, 2016
sgoldsmith@codeferm.com
"""

"""People detector using resize, frame sampling and motion ROIs.

Resizes frame, lowers sample rate and uses moving average to determine change
percent. This can result in up to ~1200% better performance and a more stable ROI.
Histogram of Oriented Gradients ([Dalal2005]) object detector is used.

sys.argv[1] = source file or will default to "../../resources/960x720.mp4" if no args passed.

@author: sgoldsmith

"""

import logging, sys, time, numpy, cv2


def inside(r, q):
    """See if one rectangle inside another"""
    rx, ry, rw, rh = r
    qx, qy, qw, qh = q
    return rx > qx and ry > qy and rx + rw < qx + qw and ry + rh < qy + qh


def padRects(image, rects, minWidth, minHeight, padSize):
    """Pad rectangles for better hit rate"""
    imgHeight, imgWidth, imgUnknown = image.shape
    paddedRects = []
    # Get consolidated image width and height from rects
    for x, y, w, h in rects:
        # Filter based on resize size if True
        if w > minWidth and h > minHeight:
            y1 = y - padSize
            if y1 < 0:
                y1 = 0
            y2 = y + h + padSize
            if y2 > imgHeight:
                y2 = imgHeight
            x1 = x - padSize
            if x1 < 0:
                x1 = 0
            x2 = x + w + padSize
            if x2 > imgWidth:
                x2 = imgWidth
            paddedRects.append([x1, y1, x2 - x1, y2 - y1])
    return paddedRects


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
    logger = logging.getLogger("PeopleDetectResize")
    logger.setLevel("INFO")
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(module)s %(message)s")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # If no args passed then default to internal file
    if len(sys.argv) < 2:
        url = "../../resources/walking.mp4"
    else:
        url = sys.argv[1]
    outputFile = "../../output/people-detect-resize-python.avi"
    videoCapture = cv2.VideoCapture(url)
    frameWidth = videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)
    frameHeight = videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    logger.info("OpenCV %s" % cv2.__version__)
    logger.info("Input file: %s" % url)
    logger.info("Output file: %s" % outputFile)
    # See if we can reduce image size
    widthDivisor = int(frameWidth / 480)
    if widthDivisor < 1:
        widthDivisor = 1
    frameResizeWidth = int(frameWidth / widthDivisor)
    frameResizeHeight = int(frameHeight / widthDivisor)
    logger.info("Resolution: %dx%d, resized to: %dx%d" % (frameWidth, frameHeight, frameResizeWidth, frameResizeHeight))
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
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
    roisWithPeople = 0    
    movingAvgImg = None
    # How many pixels in resized image
    totalPixels = frameResizeWidth * frameResizeHeight
    movementLocations = []
    start = time.time()
    paddedRects = []
    foundPeopleLocations = []
    while not lastFrame:
        ret, image = videoCapture.read()
        if ret:
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
                # Threshold to trigger motion
                if motionPercent > 2.0:
                    framesWithMotion += 1
                    # Pad rectangles for better detection
                    paddedRects = padRects(resizeImg, movementLocationsFiltered, 31, 63, 20)
                    for x, y, w, h in paddedRects:
                        # Make sure ROI is big enough for detector
                        if w > 63 and h > 127:
                            imageRoi = resizeImg[y:y + h, x:x + w]
                            # foundLocations, foundWeights = hog.detectMultiScale(imageRoi, winStride=(8, 8), padding=(16, 16), scale=1.05)
                            foundLocations, foundWeights = hog.detectMultiScale(imageRoi, winStride=(8, 8), padding=(32, 32), scale=1.05)
                            if len(foundLocations) > 0:
                                roisWithPeople += 1
                                i = 0
                                for x2, y2, w2, h2 in foundLocations:
                                    imageRoi2 = image[y * heightMultiplier:y * heightMultiplier + (h * heightMultiplier), x * widthMultiplier:x * widthMultiplier + (w * widthMultiplier)]
                                    # Draw rectangle around people
                                    cv2.rectangle(imageRoi2, (x2, y2), (x2 + (w2 * widthMultiplier), y2 + (h2 * heightMultiplier) - 1), (255, 0, 0), 2)
                                    # Print weight
                                    cv2.putText(imageRoi2, "%1.2f" % foundWeights[i], (x2, y2 - 4), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), thickness=2, lineType=cv2.LINE_AA)
                                    i += 1
                                logger.debug("Detected people locations: %s" % (foundLocations))
            else:
                skipCount -= 1
            frames += 1
            for x, y, w, h in paddedRects:
                cv2.putText(image, "%dw x %dh" % (w, h), (x * widthMultiplier, (y * heightMultiplier) - 4), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), thickness=2, lineType=cv2.LINE_AA)
                # Draw padded rectangle around motion object
                cv2.rectangle(image, (x * widthMultiplier, y * heightMultiplier),
                              ((x + w) * widthMultiplier, (y + h) * heightMultiplier),
                              (0, 255, 0), 2)
            videoWriter.write(image)
        else:
            lastFrame = True
    elapsed = time.time() - start
    logger.info("%d frames, %d frames with motion, %d ROIs with people" % (frames, framesWithMotion, roisWithPeople))
    logger.info("%4.1f FPS, elapsed time: %4.2f seconds" % (frames / elapsed, elapsed))
    del videoCapture
    del videoWriter
