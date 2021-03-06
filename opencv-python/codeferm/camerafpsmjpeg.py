"""
Copyright (c) Steven P. Goldsmith. All rights reserved.

Created by Steven P. Goldsmith on February 3, 2017
sgjava@gmail.com
"""
"""Video capture using socket and calculate FPS.

sys.argv[1] = camera index, url or will default to "-1" if no args passed.
sys.argv[2] = frames to capture, int or will default to "200" if no args passed.

Add ?dummy=param.mjpg at end of URL. For example:
http://host/?action=stream?dummy=param.mjpg

MJPEG streamer example:
mjpg_streamer -i "/usr/local/lib/mjpg-streamer/input_uvc.so -n -f 7.5 -r 1280x720" -o "/usr/local/lib/mjpg-streamer/output_http.so -w /usr/local/www"

@author: sgoldsmith

"""

import logging, sys, time, cv2, mjpegclient

from pygments.formatters.img import JpgImageFormatter

logger = logging.getLogger("camerafpsmjpeg")
logger.setLevel("INFO")
formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(module)s %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)
# If no args passed then use default camera
if len(sys.argv) < 2:
    url = "http://localhost:8080/?action=stream?dummy=param.mjpg"
    frames = 50
else:
    url = sys.argv[1]
    frames = int(sys.argv[2])
logger.info("OpenCV %s" % cv2.__version__)
logger.info("URL: %s, frames to capture: %d" % (url, frames))
socketFile, streamSock, boundary, skipLines = mjpegclient.openUrl(url, 10)
jpeg, image = mjpegclient.getFrame(socketFile, boundary, skipLines)
height, width, unknown = image.shape
logger.info("Resolution: %dx%d" % (width, height))
if width > 0 and height > 0:
    logger.info("Calculate FPS using %d frames" % frames)
    framesLeft = frames
    start = time.time()
    # Calculate FPS
    while(framesLeft > 0):
        jpeg, image = mjpegclient.getFrame(socketFile, boundary, skipLines)
        framesLeft -= 1
    elapsed = time.time() - start
    fps = frames / elapsed
    logger.info("Calculated %4.1f FPS, elapsed time: %4.2f seconds" % (fps, elapsed))
socketFile.close()
streamSock.close()
