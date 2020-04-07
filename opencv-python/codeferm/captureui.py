"""
Copyright (c) Steven P. Goldsmith. All rights reserved.

Created by Steven P. Goldsmith on December 21, 2013
sgjava@gmail.com
"""

"""A simple video capture script using imshow.

sys.argv[1] = camera index, url or will default to "-1" if no args passed.

@author: sgoldsmith

"""
# Configure logger

import logging, sys, re, socket, cv2

logger = logging.getLogger("CaptureUI")
logger.setLevel("INFO")
formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(module)s %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)
# If no args passed then use default camera
if len(sys.argv) < 2:
    url = -1
# If arg is an integer then convert to int
elif re.match(r"[-+]?\d+$", sys.argv[1]) is not None:
    url = int(sys.argv[1])
else:
    url = sys.argv[1]
# Set socket timeout in seconds (defaults to forever)
socket.setdefaulttimeout(10)    
videoCapture = cv2.VideoCapture()
# This returns True even for bad URLs
success = videoCapture.open(url)
logger.info("OpenCV %s" % cv2.__version__)
logger.info("Press [Esc] to exit")
logger.info("URL: %s" % url)
logger.info("Resolution: %dx%d" % (videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH),
                               videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
# Deal with VideoCapture always returning True otherwise it will hang on VideoCapture.grab()
if videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH) > 0 and videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT) > 0:
    cv2.namedWindow("Python Capture")
    key = -1
    # Wait for escape to be pressed
    while(key != 27 and success):
        videoCapture.grab()
        success, image = videoCapture.read()
        cv2.imshow("Python Capture", image)
        key = cv2.waitKey(1)
    cv2.destroyAllWindows()
else:
    logger.error("Unable to open device")
