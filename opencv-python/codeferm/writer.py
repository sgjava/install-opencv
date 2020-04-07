"""
Copyright (c) Steven P. Goldsmith. All rights reserved.

Created by Steven P. Goldsmith on December 23, 2013
sgjava@gmail.com
"""

"""Example of VideoWriter module.

sys.argv[1] = source file or will default to "../../resources/traffic.mp4" if no args passed.

@author: sgoldsmith

"""
# Configure logger

import logging, sys, time, cv2

logger = logging.getLogger("Writer")
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
outputFile = "../../output/writer-python.avi"
logger.info("OpenCV %s" % cv2.__version__)
logger.info("Input file: %s" % url)
logger.info("Output file: %s" % outputFile)
videoCapture = cv2.VideoCapture(url)
logger.info("Resolution: %dx%d" % (videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH),
                               videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
videoWriter = cv2.VideoWriter(outputFile, cv2.VideoWriter_fourcc(*'X264'), videoCapture.get(cv2.CAP_PROP_FPS),
                              (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))), True)
lastFrame = False
frames = 0
start = time.time()
while not lastFrame:
    ret, image = videoCapture.read()
    if ret:
        videoWriter.write(image)
        frames += 1
    else:
        lastFrame = True
elapsed = time.time() - start
logger.info("%d frames" % frames)
logger.info("%4.1f FPS, elapsed time: %4.2f seconds" % (frames / elapsed, elapsed))
del videoCapture
del videoWriter
