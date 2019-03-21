#!python
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import geom_util as geom
import braccetto_conf as bconf
import cv2
import abb
import argparse
import math
import imutils
import datetime
import time
import copy

ap = argparse.ArgumentParser()
ap.add_argument("-r", "--robot", help="enable robot mode")
ap.add_argument("-v", "--video", help="enable video mode")
ap.add_argument("-d", "--debug", help="enable debug mode")
ap.add_argument("-s", "--start", help="select starting movement")
args = vars(ap.parse_args())

ROBOT_MODE = True if args["robot"] == "y" else False
VIDEO_MODE = True if args["video"] == "y" else False
DEBUG_MODE = True if args["debug"] == "y" else False

direction_txt = None
DIRECTION_STATE = None
ROBOT_POS_X = None
ROBOT_POS_Y = None
ROBOT_POS_Z = None

if args["start"] == "l":
	direction_txt = "LEFT"
	DIRECTION_STATE = bconf.DIRECTION.LEFT
	ROBOT_POS_X = bconf.AXIS_RANGE_X[1]
	ROBOT_POS_Y = int((bconf.AXIS_RANGE_Y[0]+bconf.AXIS_RANGE_Y[1])/2)
	ROBOT_POS_Z = bconf.AXIS_RANGE_Z[1]

elif args["start"] == "r":
	direction_txt = "RIGHT"
	DIRECTION_STATE = bconf.DIRECTION.RIGHT
	ROBOT_POS_X = bconf.AXIS_RANGE_X[0]
	ROBOT_POS_Y = int((bconf.AXIS_RANGE_Y[0]+bconf.AXIS_RANGE_Y[1])/2)
	ROBOT_POS_Z = bconf.AXIS_RANGE_Z[0]

elif args["start"] == "u":
	direction_txt = "UP"
	DIRECTION_STATE = bconf.DIRECTION.UP
	ROBOT_POS_X = int((bconf.AXIS_RANGE_X[0]+bconf.AXIS_RANGE_X[1])/2)
	ROBOT_POS_Y = bconf.AXIS_RANGE_Y[0]
	ROBOT_POS_Z = int((bconf.AXIS_RANGE_Z[0]+bconf.AXIS_RANGE_Z[1])/2)

elif args["start"] == "d":
	direction_txt = "DOWN"
	DIRECTION_STATE = bconf.DIRECTION.DOWN
	ROBOT_POS_X = int((bconf.AXIS_RANGE_X[0]+bconf.AXIS_RANGE_X[1])/2)
	ROBOT_POS_Y = bconf.AXIS_RANGE_Y[1]
	ROBOT_POS_Z = int((bconf.AXIS_RANGE_Z[0]+bconf.AXIS_RANGE_Z[1])/2)

else:
	direction_txt = "DOWN"
	DIRECTION_STATE = bconf.DIRECTION.DOWN
	ROBOT_POS_X = int((bconf.AXIS_RANGE_X[0]+bconf.AXIS_RANGE_X[1])/2)
	ROBOT_POS_Y = int((bconf.AXIS_RANGE_Y[0]+bconf.AXIS_RANGE_Y[1])/2)
	ROBOT_POS_Z = int((bconf.AXIS_RANGE_Z[0]+bconf.AXIS_RANGE_Z[1])/2)

vs = None
frame = None
fps = None
(H, W) = (None, None)
centerPos = (None, None)

if ROBOT_MODE:
	a = 0
	try:
	    print ("Connecting to %s ..." % (bconf.ROBOT_IP))
	    R = abb.Robot(ip=bconf.ROBOT_IP)
	    print ("\t+ Successfully connected to %s" % (bconf.ROBOT_IP))
	    print ("\t+ %s" % (R.get_robotinfo()))
	    # R.set_speed([100,50,50,50])
	    # R.set_joints([0,0,0,0,0,0])
	except:
	    a = 1;
	    print ("\t- Error: Failed to connect to %s. Trying 127.0.0.1 now ..." % (bconf.ROBOT_IP))
	if(a == 1):
		try:
		    print ("Connecting to 127.0.0.1 ...")
		    R = abb.Robot(ip='127.0.0.1')
		except:
			print ("\t- Error: Failed to connect to 127.0.0.1. Exiting now.")
			exit(-1)

	print("Current robotic arm position ...")
	robot_get_cartesian = R.get_cartesian()
	temp_pos_x = robot_get_cartesian[0][0]
	temp_pos_y = robot_get_cartesian[0][1]
	temp_pos_z = robot_get_cartesian[0][2]
	# print("robot_get_cartesian = %s" % (robot_get_cartesian))
	print("ROBOT_POS_X = %s mm, ROBOT_POS_Y = %s mm, ROBOT_POS_Z = %s mm" % (temp_pos_x, temp_pos_y, temp_pos_z))
	R.set_speed([100,50,50,50])
	print("Initializing starting position ...")
	# R.set_cartesian([[ROBOT_POS_X, ROBOT_POS_Y, ROBOT_POS_Z], bconf.Q_ORIENTATION])
	R.set_cartesian([[1200, 0, 1200], bconf.Q_ORIENTATION])
	robot_get_cartesian = R.get_cartesian()
	temp_pos_x = robot_get_cartesian[0][0]
	temp_pos_y = robot_get_cartesian[0][1]
	temp_pos_z = robot_get_cartesian[0][2]
	print("ROBOT_POS_X = %s mm, ROBOT_POS_Y = %s mm, ROBOT_POS_Z = %s mm" % (temp_pos_x, temp_pos_y, temp_pos_z))
	# R.close()
	# exit()

if VIDEO_MODE or ROBOT_MODE:
	vs = VideoStream(src=0).start()
	time.sleep(2.0)

fps = FPS().start()

while True:
	if VIDEO_MODE or ROBOT_MODE:
		frame = vs.read()
	else:
		# frame = cv2.imread("lines.png")
		# frame = cv2.imread("blackline1.jpg")
		# frame = cv2.imread("lab_line_example.jpg")
		# frame = cv2.imread("lab_line_example_Hflip.jpg")
		# frame = cv2.imread("circletrack.png")
		frame = cv2.imread("test_direction_frame.jpg")
		# frame = cv2.imread("test_line1.jpg")
		# frame = cv2.imread("test_line2.jpg")
	frame = imutils.resize(frame, width=bconf.MAX_FRAME_WIDTH)

	if W is None or H is None:
		(H, W) = frame.shape[:2]
		centerPos = (int(W/2), int(H/2))
		crop_LRFB = (int(centerPos[0]*bconf.CROP_RATIO[0]), int(centerPos[1]*bconf.CROP_RATIO[1]), int(centerPos[0]*bconf.CROP_RATIO[2]), int(centerPos[1]*bconf.CROP_RATIO[3]))
	
	crop = None
	if DIRECTION_STATE == bconf.DIRECTION.LEFT:
		direction_txt = "LEFT"
		crop = frame[centerPos[1]-crop_LRFB[1]:centerPos[1]+crop_LRFB[1], centerPos[0]-crop_LRFB[0]:centerPos[0]]
		
	elif DIRECTION_STATE == bconf.DIRECTION.RIGHT:
		direction_txt = "RIGHT"
		crop = frame[centerPos[1]-crop_LRFB[1]:centerPos[1]+crop_LRFB[1], centerPos[0]:centerPos[0]+crop_LRFB[0]]
		
	elif DIRECTION_STATE == bconf.DIRECTION.UP:
		direction_txt = "UP"
		crop = frame[centerPos[1]-crop_LRFB[3]:centerPos[1], centerPos[0]-crop_LRFB[2]:centerPos[0]+crop_LRFB[2]]
		
	elif DIRECTION_STATE == bconf.DIRECTION.DOWN:
		direction_txt = "DOWN"
		crop = frame[centerPos[1]:centerPos[1]+crop_LRFB[3], centerPos[0]-crop_LRFB[2]:centerPos[0]+crop_LRFB[2]]
		
	# crop = frame[int(3*H/4):H, int(W/4):int(3*W/4)]
	# crop = frame[100:350, 400:550]
	# crop = frame[150:350, 200:300]

	gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

	blur = cv2.GaussianBlur(gray, (9, 9), 0)

	# ret1,th1 = cv2.threshold(blur, bconf.THRESHOLD, 255, 0)
	ret1,th1 = cv2.threshold(blur, bconf.THRESHOLD, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU) #using threshold remove noise
	ret2,th2 = cv2.threshold(th1, bconf.THRESHOLD, 255, cv2.THRESH_BINARY_INV) # invert the pixels of the image frame

	# im2,contours,hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	# im2,contours,hierarchy = cv2.findContours(th2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	contours,hierarchy = cv2.findContours(th2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
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
		if DIRECTION_STATE == bconf.DIRECTION.LEFT:
			angle = geom.get_horz_angle(p1, p2, W, H)
			shift = geom.get_vert_shift(p1[0], H)

			if angle < 45:
				DIRECTION_STATE = bconf.DIRECTION.DOWN
			elif angle > 135:
				DIRECTION_STATE = bconf.DIRECTION.UP

			gc_x = centerPos[0] - crop_LRFB[0]
			gc_y = centerPos[1] - crop_LRFB[1]

		elif DIRECTION_STATE == bconf.DIRECTION.RIGHT:
			angle = geom.get_horz_angle(p1, p2, W, H)
			shift = geom.get_vert_shift(p1[0], H)

			if angle < 45:
				DIRECTION_STATE = bconf.DIRECTION.UP
			elif angle > 135:
				DIRECTION_STATE = bconf.DIRECTION.DOWN

			gc_x = centerPos[0]
			gc_y = centerPos[1] - crop_LRFB[1]

		elif DIRECTION_STATE == bconf.DIRECTION.UP:
			angle = geom.get_vert_angle(p1, p2, W, H)
			shift = geom.get_horz_shift(p1[0], W)

			if angle < 45:
				DIRECTION_STATE = bconf.DIRECTION.RIGHT
			elif angle > 135:
				DIRECTION_STATE = bconf.DIRECTION.LEFT

			gc_x = centerPos[0] - crop_LRFB[2]
			gc_y = (centerPos[1] - crop_LRFB[3])

		elif DIRECTION_STATE == bconf.DIRECTION.DOWN:
			angle = geom.get_vert_angle(p1, p2, W, H)
			shift = geom.get_horz_shift(p1[0], W)

			if angle < 45:
				DIRECTION_STATE = bconf.DIRECTION.LEFT
			elif angle > 135:
				DIRECTION_STATE = bconf.DIRECTION.RIGHT

			gc_x = centerPos[0] - crop_LRFB[2]
			gc_y = centerPos[1]

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
		frame_edit = frame.copy()
		cv2.drawContours(frame_edit, global_contours, -1, (0,255,0), 2)
		cv2.drawContours(frame_edit, [global_box], 0, (255,0,0), 2)
		cv2.line(frame_edit, gc_p1, gc_p2, (0, 0, 255), 2)
		msg_d = "Direction : %s" % direction_txt
		msg_a = "Angle : {0}".format(int(angle))
		msg_s = "Shift : {0}".format(int(shift))
		cv2.putText(frame_edit, msg_d, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
		cv2.putText(frame_edit, msg_a, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
		cv2.putText(frame_edit, msg_s, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)

		# Add cross section line segments showing the center position within the frame
		cv2.line(frame_edit, (centerPos[0],0), (centerPos[0],H), (253,106,2), 1)
		cv2.line(frame_edit, (0,centerPos[1]), (W,centerPos[1]), (253,106,2), 1)

		# Find closest and furthest points, relative to direction
		d1 = math.sqrt(math.pow((centerPos[0]-gc_p1[0]),2)+math.pow((centerPos[1]-gc_p1[1]),2))
		d2 = math.sqrt(math.pow((centerPos[0]-gc_p2[0]),2)+math.pow((centerPos[1]-gc_p2[1]),2))
		(startPt, endPt) = (0, 0)
		if d1 < d2:
			startPt = (gc_p1[0]-centerPos[0], centerPos[1]-gc_p1[1])
			endPt = (gc_p2[0]-centerPos[0], centerPos[1]-gc_p2[1])
		else:
			startPt = (gc_p2[0]-centerPos[0], centerPos[1]-gc_p2[1])
			endPt = (gc_p1[0]-centerPos[0], centerPos[1]-gc_p1[1])

		if DEBUG_MODE:
			print("%s" % msg_d)
			print("%s" % msg_a)
			print("%s" % msg_s)
			print("p1: %s d1: %03d" % (str(gc_p1), d1))
			print("p2: %s d2: % 3d" % (str(gc_p2), d2))
			print(" startPt: \t%s\n endPt: \t%s" % (str(startPt), str(endPt)))
			print("ROBOT_POS(old): (%s, %s, %s)" % (ROBOT_POS_X, ROBOT_POS_Y, ROBOT_POS_Z))
			print(" ratioPt: \t(% 3d, % 3d)" % (int(endPt[0] / bconf.ABB_MM_PX_RATIO), int(endPt[1] / bconf.ABB_MM_PX_RATIO)))

		'''
			Update the global robot position based on direction and boundaries.
		'''
		temp_pos_x = ROBOT_POS_X + int(endPt[0] / bconf.ABB_MM_PX_RATIO)
		temp_pos_y = ROBOT_POS_Y + int(endPt[1] / bconf.ABB_MM_PX_RATIO)
		if DIRECTION_STATE == bconf.DIRECTION.LEFT:
			ROBOT_POS_X = max(temp_pos_x, bconf.AXIS_RANGE_X[0])
			ROBOT_POS_Y = max(temp_pos_y, bconf.AXIS_RANGE_Y[0]) if endPt[1] < 0 else min(temp_pos_y, bconf.AXIS_RANGE_Y[1])
			ROBOT_POS_Z = ROBOT_POS_X

		elif DIRECTION_STATE == bconf.DIRECTION.RIGHT:
			ROBOT_POS_X = min(temp_pos_x, bconf.AXIS_RANGE_X[1])
			ROBOT_POS_Y = max(temp_pos_y, bconf.AXIS_RANGE_Y[0]) if endPt[1] < 0 else min(temp_pos_y, bconf.AXIS_RANGE_Y[1])
			ROBOT_POS_Z = ROBOT_POS_X

		elif DIRECTION_STATE == bconf.DIRECTION.UP:
			ROBOT_POS_X = max(temp_pos_x, bconf.AXIS_RANGE_X[0]) if endPt[0] < 0 else min(temp_pos_x, bconf.AXIS_RANGE_X[1])
			ROBOT_POS_Y = min(temp_pos_y, bconf.AXIS_RANGE_Y[1])
			ROBOT_POS_Z = ROBOT_POS_X

		elif DIRECTION_STATE == bconf.DIRECTION.DOWN:
			ROBOT_POS_X = max(temp_pos_x, bconf.AXIS_RANGE_X[0]) if endPt[0] < 0 else min(temp_pos_x, bconf.AXIS_RANGE_X[1])
			ROBOT_POS_Y = max(temp_pos_y, bconf.AXIS_RANGE_Y[0])
			ROBOT_POS_Z = ROBOT_POS_X

		if DEBUG_MODE:
			print("ROBOT_POS(new): (%s, %s, %s)" % (ROBOT_POS_X, ROBOT_POS_Y, ROBOT_POS_Z))

		if ROBOT_MODE:
			R.set_cartesian([[ROBOT_POS_X, ROBOT_POS_Y, ROBOT_POS_Z], bconf.Q_ORIENTATION])

		cv2.imshow("frame", frame)
		# cv2.imshow("crop", crop)
		# cv2.imshow("gray", gray)
		# cv2.imshow("blur", blur)
		# cv2.imshow("th1", th1)
		# cv2.imshow("th2", th2)
		cv2.imshow("contours1", temp1)
		cv2.imshow("frame_edit", frame_edit)
	else:
		cv2.imshow("frame", frame)

	fps.update()

	if DEBUG_MODE:
		# cv2.waitKey(0)
		key = cv2.waitKey(0) & 0xFF
		if key == ord("s"):
			# timestamp = str(datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
			cv2.imwrite('test_direction_'+direction_txt+'.jpg', frame)
			cv2.imwrite('test_direction_'+direction_txt+'_edit.jpg', frame_edit)
		break
		
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break

fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

try:
	vs.stop()
except:
	pass
try:
	vs.release()
except:
	pass

cv2.destroyAllWindows()
