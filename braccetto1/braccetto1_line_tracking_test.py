#!python
from imutils.video import VideoStream
from imutils.video import FPS
from enum import Enum
import numpy as np
import geom_util as geom
import cv2
import abb
import argparse
import math
import imutils
import time
import copy

ap = argparse.ArgumentParser()
ap.add_argument("-r", "--robot", help="enable robot mode")
ap.add_argument("-v", "--video", help="enable video mode")
ap.add_argument("-d", "--debug", help="enable debug mode")
args = vars(ap.parse_args())

ROBOT_MODE = True if args["robot"] == "y" else False
VIDEO_MODE = True if args["video"] == "y" else False
DEBUG_MODE = True if args["debug"] == "y" else False

robot_ip = "192.168.125.1"
AXIS_RANGE_X = [650, 1200] # Compact = 650, Extended = 1200
AXIS_RANGE_Y = [-750, 750] # Right = -750, Left = 750
AXIS_RANGE_Z = [1200, 300] # Top = 1200, Bottom = 300
qOrientation = [0,0,1,0] # Quaternion Orientation

ROBOT_POS_X = int((AXIS_RANGE_X[0]+AXIS_RANGE_X[1])/2)
ROBOT_POS_Y = int((AXIS_RANGE_Y[0]+AXIS_RANGE_Y[1])/2)
ROBOT_POS_Z = int((AXIS_RANGE_Z[0]+AXIS_RANGE_Z[1])/2)

class DIRECTION(Enum):
	LEFT = 0
	RIGHT = 1
	FORWARD = 2
	BACKWARD = 3

DIRECTION_STATE = DIRECTION.LEFT
if DIRECTION_STATE == DIRECTION.LEFT:
	ROBOT_POS_Y = int(AXIS_RANGE_Y[1])
	ROBOT_POS_Z = AXIS_RANGE_Z[1]
elif DIRECTION_STATE == DIRECTION.RIGHT:
	ROBOT_POS_Y = int(AXIS_RANGE_Y[0])
direction_txt = None

# rho = 1
# theta = np.pi/180
threshold = 120	 	# Minimum vote it should get for it to be considered as a line.
# minLineLength = 10	# Minimum length of line. Line segments shorter than this are rejected.
# maxLineGap = 10		# Maximum allowed gap between line segments to treat them as single line.
# apertureSize = 3

MAX_FRAME_WIDTH = 800
crop_ratio = [0.75, 0.40, 0.40, 0.90]	# [ L/R(x,y), F/B(x,y) ]
abb_mm_px_ratio = 5

frame = None
fps = None
(H, W) = (None, None)
center_pos = (None, None)

vs = None
if VIDEO_MODE or ROBOT_MODE:
	vs = VideoStream(src=0).start()
	time.sleep(2.0)

if ROBOT_MODE:
	a = 0
	try:
	    print ("Connecting to %s ..." % (robot_ip))
	    R = abb.Robot(ip=robot_ip)
	    print ("\t+ Successfully connected to %s" % (robot_ip))
	    print ("\t+ %s" % (R.get_robotinfo()))
	    # R.set_joints([0,0,0,0,0,0])
	except:
	    a = 1;
	    print ("\t- Error: Failed to connect to %s. Trying 127.0.0.1 now ..." % (robot_ip))
	if(a == 1):
		try:
		    print ("Connecting to 127.0.0.1 ...")
		    R = abb.Robot(ip='127.0.0.1')
		except:
			print ("\t- Error: Failed to connect to 127.0.0.1. Exiting now.")
			exit(-1)

	robot_get_cartesian = R.get_cartesian()
	ROBOT_POS_X = robot_get_cartesian[0][0]
	ROBOT_POS_Y = robot_get_cartesian[0][1]
	ROBOT_POS_Z = robot_get_cartesian[0][2]
	print("robot_get_cartesian = %s" % (robot_get_cartesian))
	print("ROBOT_POS_X = %s mm" % (ROBOT_POS_X))
	print("ROBOT_POS_Y = %s mm" % (ROBOT_POS_Y))
	print("ROBOT_POS_Z = %s mm" % (ROBOT_POS_Z))
	R.set_speed([100,50,50,50])
	R.set_cartesian([[ROBOT_POS_X, ROBOT_POS_Y, ROBOT_POS_Z], qOrientation])
	# R.close()
	# exit()

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
		center_pos = (int(W/2), int(H/2))
		crop_LRFB = (int(center_pos[0]*crop_ratio[0]), int(center_pos[1]*crop_ratio[1]), int(center_pos[0]*crop_ratio[2]), int(center_pos[1]*crop_ratio[3]))
	
	crop = None
	if DIRECTION_STATE == DIRECTION.LEFT:
		crop = frame[center_pos[1]-crop_LRFB[1]:center_pos[1]+crop_LRFB[1], center_pos[0]-crop_LRFB[0]:center_pos[0]]
		direction_txt = "LEFT"
	elif DIRECTION_STATE == DIRECTION.RIGHT:
		crop = frame[center_pos[1]-crop_LRFB[1]:center_pos[1]+crop_LRFB[1], center_pos[0]:center_pos[0]+crop_LRFB[0]]
		direction_txt = "RIGHT"
	elif DIRECTION_STATE == DIRECTION.FORWARD:
		crop = frame[center_pos[1]-crop_LRFB[3]:center_pos[1], center_pos[0]-crop_LRFB[2]:center_pos[0]+crop_LRFB[2]]
		direction_txt = "FORWARD"
	elif DIRECTION_STATE == DIRECTION.BACKWARD:
		crop = frame[center_pos[1]:center_pos[1]+crop_LRFB[3], center_pos[0]-crop_LRFB[2]:center_pos[0]+crop_LRFB[2]]
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
	global_contours = copy.deepcopy(contours)

	C = None
	if contours is not None and len(contours) > 0:
		C = max(contours, key=cv2.contourArea)
	if C is not None:
		rect = cv2.minAreaRect(C)
		box = cv2.boxPoints(rect)
		box = np.int0(box)
		box = geom.order_box(box)
		global_box = copy.deepcopy(box)
		p1, p2 = geom.calc_box_vector(box)

		(angle,shift) = (0,0)
		(gc_x, gc_y) = (0,0)
		if DIRECTION_STATE == DIRECTION.LEFT:
			angle = 180 - geom.get_angle(p1, p2, W, H)
			shift = geom.get_vert_shift(p1[0], H)

			if angle < 45:
				DIRECTION_STATE = DIRECTION.BACKWARD
			elif angle > 135:
				DIRECTION_STATE = DIRECTION.FORWARD

			gc_x = center_pos[0] - crop_LRFB[0]
			gc_y = center_pos[1] - crop_LRFB[1]

		elif DIRECTION_STATE == DIRECTION.RIGHT:
			angle = geom.get_angle(p1, p2, W, H) + 90
			shift = geom.get_vert_shift(p1[0], H)

			if angle < 45:
				DIRECTION_STATE = DIRECTION.BACKWARD
			elif angle > 135:
				DIRECTION_STATE = DIRECTION.FORWARD

			gc_x = center_pos[0]
			gc_y = center_pos[1] - crop_LRFB[1]

		elif DIRECTION_STATE == DIRECTION.FORWARD:
			angle = geom.get_angle(p1, p2, W, H)
			shift = geom.get_horz_shift(p1[0], W)

			if angle < 45:
				DIRECTION_STATE = DIRECTION.RIGHT
			elif angle > 135:
				DIRECTION_STATE = DIRECTION.LEFT

			gc_x = center_pos[0] - crop_LRFB[2]
			gc_y = (center_pos[1] - crop_LRFB[3])

		elif DIRECTION_STATE == DIRECTION.BACKWARD:
			angle = geom.get_angle(p1, p2, W, H)
			shift = geom.get_horz_shift(p1[0], W)

			if angle < 45:
				DIRECTION_STATE = DIRECTION.LEFT
			elif angle > 135:
				DIRECTION_STATE = DIRECTION.RIGHT

			gc_x = center_pos[0] - crop_LRFB[2]
			gc_y = center_pos[1]

		# Draw on cropped image
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
		
		# Draw contours, box, and line on original image, using global coordinates
		for i1, cnt1 in enumerate(global_contours):
			for i2, cnt2 in enumerate(cnt1):
				for i3, cnt3 in enumerate(cnt2):
					global_contours[i1][i2][i3][0] += gc_x
					global_contours[i1][i2][i3][1] += gc_y
		for i1, bx1 in enumerate(global_box):
			global_box[i1][0] += gc_x
			global_box[i1][1] += gc_y
		gc_p1 = (p1[0]+gc_x, p1[1]+gc_y)
		gc_p2 = (p2[0]+gc_x, p2[1]+gc_y)
		temp2 = frame.copy()
		cv2.drawContours(temp2, global_contours, -1, (0,255,0), 2)
		cv2.drawContours(temp2, [global_box], 0, (255,0,0), 2)
		cv2.line(temp2, gc_p1, gc_p2, (0, 0, 255), 2)
		msg_d = "Direction : %s" % direction_txt
		msg_a = "Angle : {0}".format(int(angle))
		msg_s = "Shift : {0}".format(int(shift))
		cv2.putText(temp2, msg_d, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
		cv2.putText(temp2, msg_a, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
		cv2.putText(temp2, msg_s, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)

		# Find closest and furthest points, relative to direction
		d1 = math.sqrt(math.pow((center_pos[0]-gc_p1[0]),2)+math.pow((center_pos[1]-gc_p1[1]),2))
		d2 = math.sqrt(math.pow((center_pos[0]-gc_p2[0]),2)+math.pow((center_pos[1]-gc_p2[1]),2))
		(startPt, endPt) = (0, 0)
		
		if d1 < d2:
			startPt = (gc_p1[0]-center_pos[0], center_pos[1]-gc_p1[1])
			endPt = (gc_p2[0]-center_pos[0], center_pos[1]-gc_p2[1])
		else:
			startPt = (gc_p2[0]-center_pos[0], center_pos[1]-gc_p2[1])
			endPt = (gc_p1[0]-center_pos[0], center_pos[1]-gc_p1[1])

		print("p1:%s d1:%d" % (str(gc_p1), d1))
		print("p2:%s d2:%d" % (str(gc_p2), d2))
		print("startPt:%s -> endPt:%s" % (str(startPt), str(endPt)))
		print("GLOBAL_POS(old):(%s, %s, %s)" % (ROBOT_POS_X, ROBOT_POS_Y, ROBOT_POS_Z))

		if DIRECTION_STATE == DIRECTION.LEFT:
			temp_pos_x = ROBOT_POS_X + int((endPt[1] / abb_mm_px_ratio))
			ROBOT_POS_X = max(temp_pos_x, AXIS_RANGE_X[0])
			temp_pos_y = ROBOT_POS_Y + int((endPt[0] / abb_mm_px_ratio))
			ROBOT_POS_Y = min(temp_pos_y, AXIS_RANGE_Y[1])

		elif DIRECTION_STATE == DIRECTION.RIGHT:
			temp_pos_x = ROBOT_POS_X + int((endPt[1] / abb_mm_px_ratio))
			ROBOT_POS_X = max(temp_pos_x, AXIS_RANGE_X[1])
			temp_pos_y = ROBOT_POS_Y + int((endPt[0] / abb_mm_px_ratio))
			ROBOT_POS_Y = max(temp_pos_y, AXIS_RANGE_Y[0])

		print("GLOBAL_POS(new):(%s, %s, %s) temp_pos_y:%s" % (ROBOT_POS_X, ROBOT_POS_Y, ROBOT_POS_Z, temp_pos_y))

		if ROBOT_MODE:
			R.set_cartesian([[ROBOT_POS_X, ROBOT_POS_Y, ROBOT_POS_Z], qOrientation])


		# cv2.imshow("frame", frame)
		# cv2.imshow("crop", crop)
		# cv2.imshow("gray", gray)
		# cv2.imshow("blur", blur)
		# cv2.imshow("th1", th1)
		# cv2.imshow("th2", th2)
		# cv2.imshow("contours1", temp1)
		cv2.imshow("contours2", temp2)
	else:
		cv2.imshow("frame", frame)

	fps.update()

	if DEBUG_MODE:
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
