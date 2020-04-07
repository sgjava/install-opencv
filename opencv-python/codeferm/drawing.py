"""
Copyright (c) Steven P. Goldsmith. All rights reserved.

Created by Steven P. Goldsmith on June 28, 2015
sgjava@gmail.com
"""

"""Example of drawing on Mat and saving to file.

sys.argv[1] = dest file or will default to "../../output/drawing-python.png" if no args passed.

@author: sgoldsmith

"""
# Configure logger

import logging, sys, time, cv2, numpy

logger = logging.getLogger("Drawing")
logger.setLevel("INFO")
formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(module)s %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)
# If no args passed then default to internal file
if len(sys.argv) < 2:
    outputFile = "../../output/drawing-python.png"
else:
    outputFile = sys.argv[1]
logger.info("OpenCV %s" % cv2.__version__)
logger.info("Output file: %s" % outputFile)
width = 640;
height = 480;
# Make black image
mat = numpy.zeros((height, width, 3), numpy.uint8)
# Create colors
white = (255, 255, 255)
blue = (255, 0, 0)
green = (0, 255, 0)
red = (0, 0, 255)
start = time.time()
# Draw text
cv2.putText(mat, 'Python drawing', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, white, 2, cv2.LINE_AA)
# Draw line
mat = cv2.line(mat, (width // 2 - 100, height // 2 - 100), (width // 2 + 100, height // 2 + 100), white, 2)
# Draw circle
mat = cv2.circle(mat, (width // 2 - 1, height // 2 - 1), 100, red, 2)
# Draw ellipse
mat = cv2.ellipse(mat, (width // 2 - 1, height // 2 - 1), (110, 160), 45.0, 0.0, 360.0, blue, 2)
# Draw rectangle
mat = cv2.rectangle(mat, (width // 2 - 50, height // 2 - 50), (width // 2 + 50, height // 2 + 50), blue, 2)
# Draw filled rectangle
mat = cv2.rectangle(mat, (width // 2 - 40, height // 2 - 40), (width // 2 + 40, height // 2 + 40), green, cv2.FILLED)
elapsed = time.time() - start
cv2.imwrite(outputFile, mat)
logger.info("Elapsed time: %4.2f seconds" % elapsed)
