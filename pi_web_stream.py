from imutils.video import VideoStream
from flask import Response
from flask import Flask
import threading
import argparse
import time
import cv2

currentImage = None
lock = threading.Lock()

# initialize the video stream
#vs = VideoStream(usePiCamera=1).start()
vs = VideoStream(src=0).start()
time.sleep(2.0)

# initialize flask object
app = Flask(__name__)

#Example
#192.168.1.8:8000
@app.route("/")
def video_feed():
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

def generate():
	global currentImage, lock
	while True:
		with lock:
			if currentImage is None:
				continue
			(flag, encodedImage) = cv2.imencode(".jpg", currentImage)
			if not flag:
				continue

		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

def video_read():
    global vs, currentImage, lock
    while True:
        with lock:
            currentImage = vs.read()


if __name__ == '__main__':
	# argument parser
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--ip", type=str, default="0.0.0.0",
		help="ip address of the device")
	ap.add_argument("-o", "--port", type=int, default=8000,
		help="port number of the server (1024 to 65535)")
	args = vars(ap.parse_args())

	# Thread for video capture
	t = threading.Thread(target=video_read)
	t.daemon = True
	t.start()

	# Thread for web application
	app.run(host=args["ip"], port=args["port"], debug=True,
		threaded=True, use_reloader=False)

# Stop the stream object
vs.stop()