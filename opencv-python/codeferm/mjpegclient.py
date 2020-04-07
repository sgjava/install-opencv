"""
Copyright (c) Steven P. Goldsmith. All rights reserved.

Created by Steven P. Goldsmith on February 3, 2017
sgjava@gmail.com
"""

"""Socket based MJPEG frame grabber.

@author: sgoldsmith

"""

import socket, base64, numpy, cv2
from urllib.parse import urlparse


def openUrl(url, timeout):
    """Open socket"""
    # Set socket timeout
    socket.setdefaulttimeout(timeout)
    # Parse URL
    parsed = urlparse(url)
    port = parsed.port
    # Set port to default if not set
    if not port:
        port = 80
    # See if query string present
    if not parsed.query:
        path = parsed.path
    else:
        path = "%s%s%s" % (parsed.path, "?", parsed.query)   
    # See if we need to do HTTP basic access authentication
    if parsed.username is None:
        # Build HTTP header
        lines = [
            "GET %s HTTP/1.1" % path,
            "Host: %s" % parsed.hostname,
        ]
    else:
        # Base64 encode username and password
        token = base64.b64encode(("%s:%s" % (parsed.username, parsed.password)).encode('utf-8')).decode('utf-8')
        # Build HTTP header
        lines = [
            "GET %s HTTP/1.1" % path,
            "Host: %s" % parsed.hostname,
            "Authorization: Basic %s" % token,
        ]
    # AF_INET: IPv4 protocols (both TCP and UDP)
    # SOCK_STREAM: a connection-oriented, TCP byte stream
    streamSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    streamSock.connect((parsed.hostname, port))
    # Socket file in read, write, binary mode and no buffer
    socketFile = streamSock.makefile("rwb", buffering=None)
    # Send HTTP GET for MJPEG stream
    socketFile.write("\r\n".join(lines).encode('utf-8') + b"\r\n\r\n")
    socketFile.flush()
    # Read in HTTP headers
    line = socketFile.readline()
    boundary = b""
    while len(line) > 0 and line.strip() != b"" and boundary == b"":
        if line.lower().find(b"content-type: multipart") >= 0:
            parts = line.split(b":")
            if len(parts) > 1 and parts[0].lower() == b"content-type":
                # Extract boundary string from content-type
                content_type = parts[1].strip()
                boundary = content_type.split(b";")[1].split(b"=")[1]
        line = socketFile.readline()
    # See how many lines need to be skipped after 'content-length'
    while len(line) > 0 and line.strip().lower().find(b"content-length") < 0:
        line = socketFile.readline()
    # Find start of image
    skipLines = -1
    while len(line) > 0 and line.strip().lower().find(bytes.fromhex('ffd8')) != 0:
        line = socketFile.readline()
        skipLines += 1
    return socketFile, streamSock, boundary, skipLines


def getFrameLength(socketFile, boundary, skipLines):
    """Get frame length from stream"""
    line = socketFile.readline()
    # Find boundary
    while len(line) > 0 and line.count(boundary) == 0:
        line = socketFile.readline()
    length = 0
    # Read in chunk headers
    while len(line) > 0 and line.strip() != "" and length == 0:
        parts = line.split(b":")
        if len(parts) > 1 and parts[0].lower().count(b"content-length") > 0:
            # Grab chunk length
            length = int(parts[1].strip())
            # Skip lines before image data
            i = skipLines
            while i > 0:
                line = socketFile.readline()
                i -= 1
        else:
            line = socketFile.readline()
    return length


def getFrame(socketFile, boundary, skipLines):
    """Get raw frame data from stream and decode"""
    jpeg = socketFile.read(getFrameLength(socketFile, boundary, skipLines))
    return jpeg, cv2.imdecode(numpy.fromstring(jpeg, numpy.uint8), cv2.IMREAD_COLOR)
