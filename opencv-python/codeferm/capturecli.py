"""
Copyright (c) Steven P. Goldsmith. All rights reserved.

Created by Steven P. Goldsmith on December 12, 2016
sgjava@gmail.com
"""

"""A simple video capture CLI.

sys.argv[1] = camera index, url or will default to "-1" if no args passed.
sys.argv[2] = frames to capture, int or will default to "100" if no args passed.

@author: sgoldsmith

"""
# Configure logger

import logging, sys, time, re, socket, cv2

logger = logging.getLogger("CaptureCli")
logger.setLevel("INFO")
formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(module)s %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)
# If no args passed then use default camera
if len(sys.argv) < 2:
    url = -1
    frames = 200
# If arg is an integer then convert to int
elif re.match(r"[-+]?\d+$", sys.argv[1]) is not None:
    url = int(sys.argv[1])
    frames = int(sys.argv[2])
else:
    url = sys.argv[1]
    frames = int(sys.argv[2])
sampleFrames = 200
outputFile = "../../output/capturecli-python.avi"
# Set socket timeout in seconds (defaults to forever)
socket.setdefaulttimeout(10)    
videoCapture = cv2.VideoCapture()
# This returns True even for bad URLs
success = videoCapture.open(url)
logger.info("OpenCV %s" % cv2.__version__)
logger.info("Press [Esc] to exit")
logger.info("URL: %s" % url)
logger.info("Frames to capture: %d" % frames)
logger.info("Resolution: %dx%d" % (videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH),
                               videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
# Deal with VideoCapture always returning True otherwise it will hang on VideoCapture.grab()
if videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH) > 0 and videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT) > 0:
    logger.info("Calculate FPS using %d frames" % sampleFrames)
    videoWriter = cv2.VideoWriter(outputFile, cv2.VideoWriter_fourcc(*'X264'), videoCapture.get(cv2.CAP_PROP_FPS),
                              (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))), True)
    framesLeft = sampleFrames
    start = time.time()
    # Calculate FPS
    while(framesLeft > 0):
        videoCapture.grab()
        success, image = videoCapture.read()
        if success:
            videoWriter.write(image)
        else:
            logger.error("Failed to read image")
        framesLeft -= 1
    elapsed = time.time() - start
    fps = sampleFrames / elapsed
    logger.info("Calculated %4.1f FPS, elapsed time: %4.2f seconds" % (fps, elapsed))
    del videoWriter
    videoWriter = cv2.VideoWriter(outputFile, cv2.VideoWriter_fourcc(*'X264'), fps,
                              (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))), True)
    framesLeft = frames
    start = time.time()
    # Wait for no frames left
    while(framesLeft > 0):
        videoCapture.grab()
        success, image = videoCapture.read()
        if success:
            videoWriter.write(image)
        else:
            logger.error("Failed to read image")
        framesLeft -= 1
    elapsed = time.time() - start
    logger.info("Captured %4.1f FPS, elapsed time: %4.2f seconds" % (frames / elapsed, elapsed))
    del videoWriter
else:
    logger.error("Unable to open device")
del videoCapture
