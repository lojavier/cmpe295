#!python
import cv2
from imutils.video import VideoStream
from imutils.video import FPS
from enum import Enum
import numpy as np
import math
import imutils
import time
import geom_util as geom

class DIRECTION(Enum):
	LEFT = 0
	RIGHT = 1
	FORWARD = 2
	BACKWARD = 3

rho = 1
theta = np.pi/180
threshold = 120	 	# Minimum vote it should get for it to be considered as a line.
minLineLength = 10	# Minimum length of line. Line segments shorter than this are rejected.
maxLineGap = 10		# Maximum allowed gap between line segments to treat them as single line.
apertureSize = 3
MAX_FRAME_WIDTH = 800
DIRECTION_STATE = DIRECTION.RIGHT
direction_txt = None
trim_offset = int(MAX_FRAME_WIDTH/4)

frame = None
fps = None
(H, W) = (None, None)
(center_x, center_y) = (None, None)

vs = None
# vs = VideoStream(src=0).start()
# time.sleep(2.0)

fps = FPS().start()

while True:
	# frame = vs.read()
	# frame = cv2.imread("lines.png")
	# frame = cv2.imread("blackline1.jpg")
	frame = cv2.imread("lab_line_example.jpg")
	# frame = cv2.imread("lab_line_example_Hflip.jpg")
	# frame = cv2.imread("circletrack.png")
	# frame = cv2.imread("curveline.png")
	frame = imutils.resize(frame, width=MAX_FRAME_WIDTH)

	if W is None or H is None:
		(H, W) = frame.shape[:2]
		(center_x, center_y) = (int(W/2), int(H/2))
	
	crop = None
	if DIRECTION_STATE == DIRECTION.LEFT:
		crop = frame[center_y-trim_offset:center_y+trim_offset, 0:center_x]
		direction_txt = "LEFT"
	elif DIRECTION_STATE == DIRECTION.RIGHT:
		crop = frame[center_y-trim_offset:center_y+trim_offset, center_x:W]
		direction_txt = "RIGHT"
	elif DIRECTION_STATE == DIRECTION.FORWARD:
		crop = frame[0:center_y, center_x-trim_offset:center_x+trim_offset]
		direction_txt = "FORWARD"
	elif DIRECTION_STATE == DIRECTION.BACKWARD:
		crop = frame[center_y:H, center_x-trim_offset:center_x+trim_offset]
		direction_txt = "BACKWARD"
	# crop = frame[int(3*H/4):H, int(W/4):int(3*W/4)]
	# crop = frame[100:350, 400:550]
	# crop = frame[150:350, 200:300]

	gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

	blur = cv2.GaussianBlur(gray, (9, 9), 0)

	# ret1,th1 = cv2.threshold(blur, threshold, 255, 0)
	ret1,th1 = cv2.threshold(blur, threshold, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU) #using threshold remave noise
	ret2,th2 = cv2.threshold(th1, threshold, 255, cv2.THRESH_BINARY_INV) # invert the pixels of the image frame

	# im2,contours,hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	im2,contours,hierarchy = cv2.findContours(th2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	# global_contours = contours.copy()
	global_contours = list(contours)
	# print("len(contours)=%d" % (len(contours)))
	# for cnt1 in contours:
	for i1, cnt1 in enumerate(global_contours):
		if len(cnt1) > 0:
			for i2, cnt2 in enumerate(cnt1):
				if len(cnt2) > 0:
					for i3, cnt3 in enumerate(cnt2):
						global_contours[i1][i2][i3][0] += center_x
						global_contours[i1][i2][i3][1] += center_y
	print("global_contours=%s" % (global_contours))
	print("contours=%s\n" % (contours))
	exit()

	C = None
	if contours is not None and len(contours) > 0:
		C = max(contours, key=cv2.contourArea)
	if C is not None:
		rect = cv2.minAreaRect(C)
		box = cv2.boxPoints(rect)
		box = np.int0(box)
		box = geom.order_box(box)
		p1, p2 = geom.calc_box_vector(box)

		(angle,shift) = (0,0)
		if DIRECTION_STATE == DIRECTION.LEFT:
			angle = 180 - geom.get_angle(p1, p2, W, H)
			shift = geom.get_vert_shift(p1[0], H)
			if angle < 45:
				DIRECTION_STATE = DIRECTION.BACKWARD
			elif angle > 135:
				DIRECTION_STATE = DIRECTION.FORWARD

		elif DIRECTION_STATE == DIRECTION.RIGHT:
			angle = geom.get_angle(p1, p2, W, H) + 90
			shift = geom.get_vert_shift(p1[0], H)
			if angle < 45:
				DIRECTION_STATE = DIRECTION.BACKWARD
			elif angle > 135:
				DIRECTION_STATE = DIRECTION.FORWARD

		elif DIRECTION_STATE == DIRECTION.FORWARD:
			angle = geom.get_angle(p1, p2, W, H)
			shift = geom.get_horz_shift(p1[0], W)
			if angle < 45:
				DIRECTION_STATE = DIRECTION.RIGHT
			elif angle > 135:
				DIRECTION_STATE = DIRECTION.LEFT

		elif DIRECTION_STATE == DIRECTION.BACKWARD:
			angle = geom.get_angle(p1, p2, W, H)
			shift = geom.get_horz_shift(p1[0], W)
			if angle < 45:
				DIRECTION_STATE = DIRECTION.LEFT
			elif angle > 135:
				DIRECTION_STATE = DIRECTION.RIGHT

		temp1 = crop.copy()
		cv2.drawContours(temp1, contours, -1, (0,255,0), 2)
		cv2.drawContours(temp1, [box], 0, (255,0,0), 2)
		cv2.line(temp1, p1, p2, (0, 0, 255), 2)
		msg_d = "Direction : %s" % direction_txt
		msg_a = "Angle : {0}".format(int(angle))
		msg_s = "Shift : {0}".format(int(shift))
		cv2.putText(temp1, msg_d, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (248,24,148), 2)
		cv2.putText(temp1, msg_a, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (248,24,148), 2)
		cv2.putText(temp1, msg_s, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (248,24,148), 2)


		temp2 = frame.copy()
		cv2.drawContours(temp2, contours, -1, (0,255,0), 2)
		cv2.drawContours(temp2, [box], 0, (255,0,0), 2)
		cv2.line(temp2, p1, p2, (0, 0, 255), 2)


	cv2.imshow("frame", frame)
	# cv2.imshow("crop", crop)
	# cv2.imshow("gray", gray)
	# cv2.imshow("blur", blur)
	# cv2.imshow("th1", th1)
	# cv2.imshow("th2", th2)
	cv2.imshow("contours1", temp1)
	cv2.imshow("contours2", temp2)

	fps.update()

	cv2.waitKey(0)
	break
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break

try:
	vs.stop()
except:
	pass
try:
	vs.release()
except:
	pass

cv2.destroyAllWindows()
